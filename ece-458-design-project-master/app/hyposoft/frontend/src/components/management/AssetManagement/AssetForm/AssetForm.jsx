import React, {useState, useRef, useContext} from "react";
import {Formik} from "formik";
import {Form, Button, Typography, Row, Col, Divider} from "antd";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import SubmitButton from "../../../utility/formik/SubmitButton";
import InputNumber from "../../../utility/formik/InputNumber";
import Input from "../../../utility/formik/Input";
import TextArea from "../../../utility/formik/TextArea";
import VSpace from "../../../utility/VSpace";
import Select from "../../../utility/formik/Select";
import {getModel, getModelPicklist} from "../../../../api/model";
import {getSites} from "../../../../api/site";
import {getUserList} from "../../../../api/auth";
import {
    getAsset,
    createAsset,
    updateAsset,
    deleteAsset,
    decommissionAsset,
} from "../../../../api/asset";
import {schema} from "./AssetSchema";
import NetworkGraph from "./NetworkGraph";
import LocationTypeSelect from "./LocationTypeSelect";
import {useHistory, useLocation} from "react-router-dom";
import NetworkPowerActionButtons from "../NetworkPowerActionButtons";
import useRedirectOnCPChange from "../../../utility/useRedirectOnCPChange";
import RackMounts from "./RackMounts";
import ChassisMounts from "./ChassisMounts";
import Offline from "./Offline";
import ColorPicker from "../../ModelManagement/ModelForm/ColorPicker";
import ChassisView from "../ChassisView";
import FormDebugger from "../../../utility/formik/FormDebugger";
import styled from "styled-components";
import ConfigureUserPermissions, {
    CheckOwnerPermissions,
    CheckSitePermissions
} from "../../../utility/ConfigurePermissions";
import {AuthContext} from "../../../../contexts/contexts";

const InputBlackPlaceholder = styled(Input)`
  ::placeholder {
    color: rgba(0, 0, 0, 0.65);
  }
`;

const InputNumberBlackPlaceholder = styled(InputNumber)`
  ::placeholder {
    color: rgba(0, 0, 0, 0.65);
  }
`;

function AssetForm({id, origin}) {
    const history = useHistory();
    const { user } = useContext(AuthContext);

    const query = Object.fromEntries(
        new URLSearchParams(useLocation().search).entries(),
    );

    const locked = useRef(true);
    // prevent original fields triggering overwrite on original fields

    const [asset, setAsset] = useState(null);
    const [modelPickList, setModelPickList] = useState([]);
    const [selectedModel, setSelectedModel] = useState(null);
    const [siteList, setSiteList] = useState([]);
    const [users, setUsers] = useState([]);


    const permittedSitesAsString = user?.permission?.site_perm;
    const permittedSitesAsArray = permittedSitesAsString.split(",");

    useRedirectOnCPChange(origin);

    React.useEffect(() => {
        getModelPicklist().then(setModelPickList);
        if (!!user?.permission?.admin_perm) {
            getSites().then(setSiteList);
        }
        else {
            getSites().then(sites =>
                setSiteList(sites.filter(s => permittedSitesAsArray.includes(s?.abbr))))
            getUserList().then(setUsers);
        }

        if (id) {
            getAsset(id).then(asset => {
                setAsset(asset);
                setTimeout(() => {
                    locked.current = false;
                }, 1000);
            });
        } else {
            setAsset(schema.default());
            setTimeout(() => {
                locked.current = false;
            }, 1000);
        }
    }, []);

    //configure permissions
    const config = ConfigureUserPermissions();
    console.log("id used in asset form", id);
    const doDisplayCUDButtons = config.canAssetCUDD && CheckSitePermissions(asset?.location?.site);
    //const doDisplayCUDButtons = config.canAssetCUDD;
    console.log("doDisplayCUDButtons", doDisplayCUDButtons);
    const doDisplayPowerButtons = config.canAssetPower || CheckOwnerPermissions(asset);
    console.log("doDisplayPowerButtons", doDisplayPowerButtons);

    React.useEffect(() => {
        if (asset?.itmodel) handleModelSelect(asset.itmodel);
    }, [asset?.itmodel]);

    async function handleModelSelect(id) {
        const model = await getModel(id);
        setSelectedModel(model);
        return model;
    }

    // submit

    async function handleCreate(fields) {
        await createAsset(fields);
        history.push(origin);
        window.location.reload();
    }

    async function handleUpdate(fields) {
        const {id: newID} = await updateAsset(id, fields);
        history.push(origin + "/" + newID);
        window.location.reload();
    }

    async function handleDelete() {
        await deleteAsset(id);
        history.push(origin);
        window.location.reload();
    }

    async function handleDecommission() {
        await decommissionAsset(id);
        history.push(origin);
        window.location.reload();
    }

    return asset ? (
        <div>
            {asset.power_state != null && (
                <div>
                    {doDisplayPowerButtons ? (
                        <NetworkPowerActionButtons assetID={asset.id} displayState/>)
                        : null};
                    <VSpace height="16px"/>
                </div>
            )}
            <Row>
                <Col md={8}>
                    <Formik
                        validationSchema={schema}
                        initialValues={asset}
                        initialErrors={query}
                        initialTouched={query}
                        onSubmit={id ? handleUpdate : handleCreate}
                    >
                        {props => (
                            <Form>
                                <ItemWithLabel name="asset_number" label="Asset #">
                                    <InputNumber name="asset_number" min={100000} max={999999}/>
                                </ItemWithLabel>

                                <ItemWithLabel name="hostname" label="Hostname">
                                    <Input name="hostname"/>
                                </ItemWithLabel>

                                <ItemWithLabel name="itmodel" label="Model">
                                    <Select
                                        name="itmodel"
                                        options={modelPickList.map(({id, str}) => {
                                            return {value: id, text: str};
                                        })}
                                        onChange={handleModelSelect}
                                    />
                                    {selectedModel?.id && (
                                        <a href={`/#/models/${selectedModel.id}`}>
                                            View model details
                                        </a>
                                    )}
                                </ItemWithLabel>

                                <Divider>Upgrades</Divider>

                                <h4>* Upgraded fields are shown in orange</h4>

                                <ItemWithLabel
                                    name="display_color"
                                    label="Display Color"
                                    color={
                                        props.values.display_color != null ? "orange" : "black"
                                    }
                                >
                                    <ColorPicker
                                        name="display_color"
                                        nullable
                                        placeholder={selectedModel?.display_color}
                                    />
                                </ItemWithLabel>

                                <ItemWithLabel
                                    name="cpu"
                                    label="CPU"
                                    color={props.values.cpu != null ? "orange" : "black"}
                                >
                                    <InputBlackPlaceholder
                                        name="cpu"
                                        nullIfBlank
                                        placeholder={selectedModel?.cpu}
                                    />
                                </ItemWithLabel>

                                <ItemWithLabel
                                    name="memory"
                                    label="Memory"
                                    color={props.values.memory != null ? "orange" : "black"}
                                >
                                    <InputNumberBlackPlaceholder
                                        name="memory"
                                        placeholder={selectedModel?.memory}
                                    />
                                </ItemWithLabel>

                                <ItemWithLabel
                                    name="storage"
                                    label="Storage"
                                    color={props.values.storage != null ? "orange" : "black"}
                                >
                                    <InputBlackPlaceholder
                                        name="storage"
                                        nullIfBlank
                                        placeholder={selectedModel?.storage}
                                    />
                                </ItemWithLabel>

                                <Divider/>

                                <ItemWithLabel name="location.tag" label="Location">
                                    <LocationTypeSelect model={selectedModel} locked={locked}/>
                                </ItemWithLabel>

                                {props.values.location.tag === "rack-mount" ? (
                                    <RackMounts siteList={siteList} model={selectedModel}/>
                                ) : props.values.location.tag === "chassis-mount" ? (
                                    <ChassisMounts siteList={siteList}/>
                                ) : props.values.location.tag === "offline" ? (
                                    <Offline siteList={siteList}/>
                                ) : null}

                                <Divider/>

                                <ItemWithLabel name="owner" label="Owner">
                                    <Select
                                        name="owner"
                                        options={users.map(({id, username}) => {
                                            return {value: id, text: username};
                                        })}
                                    />
                                </ItemWithLabel>

                                <ItemWithLabel name="comment" label="Comment">
                                    <TextArea name="comment" rows={5}/>
                                </ItemWithLabel>

                                {doDisplayCUDButtons ? (
                                    <SubmitButton ghost type="primary" block>
                                        {id ? "Update" : "Create"}
                                        <VSpace height="16px"/>
                                    </SubmitButton>
                                ) : null}


                                {id && (
                                    <>
                                        <VSpace height="16px"/>
                                        {doDisplayCUDButtons ? (
                                            <Button ghost type="danger" onClick={handleDelete} block>
                                                Delete
                                            </Button>
                                        ) : null}
                                        <VSpace height="16px"/>
                                        {doDisplayCUDButtons ? (
                                            <Button
                                                ghost
                                                type="primary"
                                                onClick={() => {
                                                    if (confirm("You sure?")) {
                                                        handleDecommission();
                                                    }
                                                }}
                                                block
                                            >
                                                Decommission
                                            </Button>
                                        ) : null}
                                    </>
                                )}
                            </Form>
                        )}
                    </Formik>
                </Col>
            </Row>

            {id && asset.location.tag !== "offline" && (
                <div>
                    <div>
                        <VSpace height="32px"/>
                        <Typography.Title level={4}>Network graph</Typography.Title>
                        <NetworkGraph assetID={id} networkGraph={asset.network_graph}/>
                    </div>
                    <div>
                        <VSpace height="32px"/>
                        <ChassisView assetID={id}/>
                    </div>
                </div>
            )}
        </div>
    ) : null;
}

export default AssetForm;
