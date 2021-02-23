import React from "react";
import { Typography, Row, Col } from "antd";
import UserForm from "./UserForm";

function CreateUserPage() {
  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Create User</Typography.Title>
      <Row>
        <Col md={8}>
          <UserForm />
        </Col>
      </Row>
    </div>
  );
}

export default CreateUserPage;
