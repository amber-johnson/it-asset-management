import React from "react";
import { Typography } from "antd";
import { useLocation } from "react-router-dom";
import { getChangePlanActions } from "../../../api/changeplan";
import VSpace from "../../utility/VSpace";

function WorkOrderPage() {
  const cpID = new URLSearchParams(useLocation().search).get("cp_id");

  const [actions, setActions] = React.useState([]);

  React.useEffect(() => {
    getChangePlanActions(cpID).then(setActions);
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title>Work Order</Typography.Title>
      {actions.map((action, idx) => (
        <div key={idx}>
          {idx + 1}: {action}
          <VSpace height="8px" />
        </div>
      ))}
    </div>
  );
}

export default WorkOrderPage;
