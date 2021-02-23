import React from "react";
import { Typography } from "antd";
import AssetForm from "./AssetForm/AssetForm";

function CreateAssetPage() {
  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Create Asset</Typography.Title>
      <AssetForm origin="/assets" />
    </div>
  );
}

export default CreateAssetPage;
