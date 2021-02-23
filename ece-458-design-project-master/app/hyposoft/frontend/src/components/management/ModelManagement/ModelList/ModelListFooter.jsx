import React, {useContext} from "react";
import {AuthContext} from "../../../../contexts/contexts";
import {useHistory} from "react-router-dom";
import {PlusOutlined} from "@ant-design/icons";
import CreateTooltip from "../../../utility/CreateTooltip";
import {Button} from "antd";


function ModelListFooter() {
    const history = useHistory();

    function onCreate() {
        history.push("/models/create");
    }

    return (
        <div>
            <Button onClick={onCreate}>
                <PlusOutlined/>
            </Button>
        </div>
    );
}

export default ModelListFooter;
