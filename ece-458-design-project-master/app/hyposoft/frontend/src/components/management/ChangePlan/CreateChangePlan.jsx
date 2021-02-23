import React from "react";
import { Typography, Input, Button, Row, Col } from "antd";
import VSpace from "../../utility/VSpace";
import { createChangePlan } from "../../../api/changeplan";
import { useHistory } from "react-router-dom";
import { ChangePlanContext } from "../../../contexts/contexts";

function CreateChangePlan() {
  const history = useHistory();
  const [name, setName] = React.useState("");
  const { refresh } = React.useContext(ChangePlanContext);

  async function handleCreate() {
    await createChangePlan(name);
    refresh();
    history.push("/changeplan");
  }

  return (
    <div style={{ padding: "16px" }}>
      <Typography.Title level={3}>Create Change Plan</Typography.Title>

      <VSpace height="16px" />

      <Row>
        <Col md={8}>
          <Typography.Paragraph>Name</Typography.Paragraph>
          <Input value={name} onChange={e => setName(e.target.value)} />

          <VSpace height="16px" />

          <Button onClick={handleCreate}>Create</Button>
        </Col>
      </Row>
    </div>
  );
}

export default CreateChangePlan;
