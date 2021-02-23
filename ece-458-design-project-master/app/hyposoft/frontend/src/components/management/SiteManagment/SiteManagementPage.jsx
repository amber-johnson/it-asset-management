import React, {useContext} from "react";
import {Typography, List, Card, Input, Button, Icon, Radio} from "antd";
import {SiteContext} from "../../../contexts/contexts";
import {
    updateSite,
    deleteSite,
    createSite,
    getSites,
} from "../../../api/site";
import useTrigger from "../../utility/useTrigger";
import {
    CloseOutlined,
    DeleteOutlined,
    PlusOutlined,
    EditOutlined,
} from "@ant-design/icons";
import useRedirectOnCPChange from "../../utility/useRedirectOnCPChange";
import VSpace from "../../utility/VSpace";
import ConfigureUserPermissions from "../../utility/ConfigurePermissions";

function SiteCard({site, onUpdate, onRemove, disabled}) {

    //configure permissions
    const config = ConfigureUserPermissions();
    const doDisplay = config.canAssetCUDD;
    console.log("canSiteCUD", doDisplay);

    const [isEditing, setIsEditing] = React.useState(false);
    const [draft, setDraft] = React.useState(null);

    console.log("draft", draft);

    function confirmUpdate() {
        onUpdate(draft);
        setIsEditing(false);
    }

    React.useEffect(() => {
        setDraft({...site});
    }, [site.id, site.name, site.abbr, site.type]);

    const Actions = isEditing
        ? [<Button onClick={confirmUpdate}>Confirm</Button>]
        : [];

    const ExtraButtons = (
        <>
            <Button
                size="small"
                shape="circle"
                onClick={() => setIsEditing(!isEditing)}
                disabled={disabled}
            >
                {isEditing ? <CloseOutlined/> : <EditOutlined/>}
            </Button>
            <Button
                style={{marginLeft: 4}}
                size="small"
                shape="circle"
                type="danger"
                disabled={disabled}
                onClick={() => {
                    if (confirm("You sure?")) {
                        onRemove(site.id);
                    }
                }}
            >
                <DeleteOutlined/>
            </Button>
        </>
    );

    if (!draft) return null;

    return (
        <Card title={site.abbr}
              extra={doDisplay ? ExtraButtons : null}
              actions={Actions}>
            {isEditing ? (
                <>
                    <h4>Name</h4>
                    <Input
                        size="small"
                        value={draft.name}
                        onChange={e => setDraft({...draft, name: e.target.value})}
                        onPressEnter={confirmUpdate}
                    />
                    <h4>Abbreviated Name</h4>
                    <Input
                        size="small"
                        value={draft.abbr}
                        onChange={e => setDraft({...draft, abbr: e.target.value})}
                        onPressEnter={confirmUpdate}
                    />
                    <h4>Type</h4>
                    <Radio.Group
                        value={draft.type}
                        onChange={e => setDraft({...draft, type: e.target.value})}
                    >
                        <Radio value="datacenter">datacenter</Radio>
                        <Radio value="offline-storage">offline-storage</Radio>
                    </Radio.Group>
                </>
            ) : (
                <>
                    <h4>Name</h4>
                    <p>{site.name}</p>
                    <h4>Abbreviated Name</h4>
                    <p>{site.abbr}</p>
                    <h4>Type</h4>
                    <p>{site.type}</p>
                </>
            )}
        </Card>
    );
}

function AddCard({onCreate, disabled}) {

    //configure permissions
    const config = ConfigureUserPermissions();
    const doDisplay = config.canSiteCUD;
    console.log("canSiteCUD", doDisplay);

    return doDisplay ? (
            <Card
                style={{padding: 0, height: "100px"}}
                bodyStyle={{
                    padding: 0,
                    width: "100%",
                    height: "100%",
                }}
            >
                <Button
                    style={{width: "100%", height: "100%"}}
                    onClick={onCreate}
                    disabled={disabled}
                >
                    <PlusOutlined/>
                    Add Site
                </Button>
            </Card>
        )
        :
        (null
        );
}

function GhostCard({onCreate, onCancel}) {
    const [draft, setDraft] = React.useState({
        name: "",
        abbr: "",
        type: "datacenter",
    });

    function confirmCreate() {
        onCreate(draft);
    }

    const Actions = [<Button onClick={confirmCreate}>Confirm</Button>];

    const ExtraButtons = (
        <Button
            style={{marginLeft: 4}}
            size="small"
            shape="circle"
            onClick={onCancel}
        >
            <CloseOutlined/>
        </Button>
    );

    return (
        <Card title={draft.abbr} extra={ExtraButtons} actions={Actions}>
            <h4>Name</h4>
            <Input
                size="small"
                value={draft.name}
                onChange={e => setDraft({...draft, name: e.target.value})}
                onPressEnter={confirmCreate}
            />
            <h4>Abbreviated Name</h4>
            <Input
                size="small"
                value={draft.abbr}
                onChange={e => setDraft({...draft, abbr: e.target.value})}
                onPressEnter={confirmCreate}
            />
            <VSpace height="8px"/>
            <h4>Type</h4>
            <Radio.Group
                value={draft.type}
                onChange={e => setDraft({...draft, type: e.target.value})}
            >
                <Radio value="datacenter">datacenter</Radio>
                <Radio value="offline-storage">offline-storage</Radio>
            </Radio.Group>
        </Card>
    );
}

function SiteManagementPage() {
    const [isAdding, setIsAdding] = React.useState(false);
    const showGhostCard = () => setIsAdding(true);
    const showAddCard = () => setIsAdding(false);

    const [sites, setSites] = React.useState([]);
    const [trigger, fireTrigger] = useTrigger();
    const {site, setSiteByID, refresh} = useContext(SiteContext);

    React.useEffect(() => {
        getSites().then(setSites);
        refresh();
    }, [trigger]);

    useRedirectOnCPChange();

    const contextSiteID = site?.id;

    function handleUpdate({id, name, abbr, type}) {
        updateSite(id, {name, abbr, type}).then(fireTrigger);
    }

    function handleDelete(id) {
        deleteSite(id)
            .then(() => {
                contextSiteID === id && setSiteByID(null);
            })
            .then(fireTrigger);
    }

    function handleCreate(fields) {
        createSite(fields)
            .then(fireTrigger)
            .then(showAddCard);
    }

    function createGhost() {
        showGhostCard();
    }

    const dataSource = [...sites, isAdding ? "ghost" : "add"]; // the last one for +

    return (
        <div style={{padding: 16}}>
            <Typography.Title level={3}>Sites</Typography.Title>
            <List
                grid={{
                    gutter: 16,
                    xs: 1,
                    sm: 2,
                    md: 4,
                    lg: 4,
                    xl: 6,
                    xxl: 3,
                }}
                dataSource={dataSource}
                renderItem={site => {
                    switch (site) {
                        case "add":
                            return (
                                <List.Item>
                                    <AddCard onCreate={createGhost}/>
                                </List.Item>
                            );
                        case "ghost":
                            return (
                                <List.Item>
                                    <GhostCard onCreate={handleCreate} onCancel={showAddCard}/>
                                </List.Item>
                            );
                        default:
                            return (
                                <List.Item>
                                    <SiteCard
                                        site={site}
                                        onUpdate={handleUpdate}
                                        onRemove={handleDelete}
                                    />
                                </List.Item>
                            );
                    }
                }}
            />
        </div>
    );
}

export default SiteManagementPage;
