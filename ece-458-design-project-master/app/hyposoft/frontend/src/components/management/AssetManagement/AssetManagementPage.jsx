import React from "react";
import { Typography, Button } from "antd";
import AssetList from "./AssetList/AssetList";

function AssetManagementPage() {
    return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Assets</Typography.Title>
      <AssetList />
    </div>

  );
}

export default AssetManagementPage;
