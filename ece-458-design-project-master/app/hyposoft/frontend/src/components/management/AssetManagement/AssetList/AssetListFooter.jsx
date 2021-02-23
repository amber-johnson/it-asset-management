import React, {useContext} from "react";
import {AuthContext} from "../../../../contexts/contexts";
import {useHistory} from "react-router-dom";
import {PlusOutlined, PrinterOutlined} from "@ant-design/icons";
import {Button} from "antd";
import ConfigureUserPermissions from "../../../utility/ConfigurePermissions";

function AssetListFooter({selectedAssets}) {
    const history = useHistory();
    //const { user } = useContext(AuthContext);

    //configure permissions
    const config = ConfigureUserPermissions();
    const doDisplay = config.canAssetCUDD;
    console.log("canAssetCUDD", doDisplay);

    function onCreate() {
        history.push("/assets/create");
    }

    function onPrint() {
        history.push(`/assets/print_view?asset_ids=${selectedAssets.join(",")}`);
    }

    return doDisplay ? (
            <div>
                <Button onClick={onCreate}>
                    <PlusOutlined/>
                </Button>
                <Button onClick={onPrint}>
                    <PrinterOutlined/>
                </Button>
            </div>
        )
        : (
            <div>
                <Button onClick={onPrint}>
                    <PrinterOutlined/>
                </Button>
            </div>
        );

}

export default AssetListFooter;
