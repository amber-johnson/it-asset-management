import React from "react";
import { Typography, Button } from "antd";
import DecommissionList from "./DecommissionList/DecommissionList";


function DecommissionManagementPage() {

    return (
        <div style={{ padding: 16 }}>
            <Typography.Title level={3}>Decommissioned Assets</Typography.Title>
            <DecommissionList/>

        </div>
    );
}

export default DecommissionManagementPage;
