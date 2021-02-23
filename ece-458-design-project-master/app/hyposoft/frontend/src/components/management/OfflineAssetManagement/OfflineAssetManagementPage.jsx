import React from "react";
import { Typography } from "antd";
import AssetList from "../AssetManagement/AssetList/AssetList";

function OfflineAssetManagementPage() {
  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Offline Assets</Typography.Title>
      <AssetList forOffline />
    </div>
  );
}

export default OfflineAssetManagementPage;
