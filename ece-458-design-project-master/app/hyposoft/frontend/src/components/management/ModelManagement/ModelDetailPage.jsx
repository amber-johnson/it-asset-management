import React from "react";
import { useParams } from "react-router-dom";
import { Typography, Row, Col } from "antd";
import ModelForm from "./ModelForm/ModelForm";
import VSpace from "../../utility/VSpace";
import AssetList from "../AssetManagement/AssetList/AssetList";

function ModelDetailPage() {
  const { id } = useParams();

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Model Details</Typography.Title>
      <Row>
        <Col md={8}>
          <ModelForm id={id} />
        </Col>
      </Row>
      <VSpace height="32px" />
      <Typography.Title level={4}>Assets of this model</Typography.Title>
      <AssetList modelID={id} />
    </div>
  );
}

export default ModelDetailPage;
