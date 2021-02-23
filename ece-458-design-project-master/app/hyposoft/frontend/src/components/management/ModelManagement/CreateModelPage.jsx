import React from "react";
import { Typography, Row, Col } from "antd";
import ModelForm from "./ModelForm/ModelForm";

function CreateModelPage() {
  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Create Model</Typography.Title>
      <Row>
        <Col md={8}>
          <ModelForm />
        </Col>
      </Row>
    </div>
  );
}

export default CreateModelPage;
