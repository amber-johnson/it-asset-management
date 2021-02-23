import React from "react";
import { Typography } from "antd";
import ModelList from "./ModelList/ModelList";

function ModelManagementPage() {
  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Models</Typography.Title>
      <ModelList />
    </div>
  );
}

export default ModelManagementPage;
