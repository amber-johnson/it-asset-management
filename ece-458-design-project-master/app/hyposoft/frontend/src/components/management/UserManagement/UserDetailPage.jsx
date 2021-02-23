import React from "react";
import { useParams } from "react-router-dom";
import { Typography, Row, Col } from "antd";
import UserForm from "./UserForm";

function UserDetailPage() {
  const { id } = useParams();

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>User Details</Typography.Title>
      <Row>
        <Col md={8}>
          <UserForm id={id} />
        </Col>
      </Row>
    </div>
  );
}

export default UserDetailPage;
