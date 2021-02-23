import React from "react";
import { Typography, Table, Button } from "antd";
import styled from "styled-components";
import { getChangePlanList, executeChangePlan } from "../../../api/changeplan";
import { PlusOutlined } from "@ant-design/icons";
import { useHistory } from "react-router-dom";
import { ChangePlanContext } from "../../../contexts/contexts";

const CPTable = styled(Table)`
  cursor: pointer;
`;

function preventing(op, onSuccess) {
  return e => {
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation();
    op(e).then(onSuccess);
  };
}

const cpColumns = execute => [
  {
    title: "Name",
    dataIndex: "name",
    sorter: false,
  },
  {
    title: "Executed At",
    key: "executed_at",
    render: (t, r) => {
      return r.executed_at ?? "N/A";
    },
    sorter: false,
  },
  {
    title: "Actions",
    key: "actions",
    render: (t, r) => {
      return (
        !r.executed_at && (
          <Button onClick={preventing(() => execute(r.id))}>Execute</Button>
        )
      );
    },
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
];

function ChangePlanList() {
  const history = useHistory();
  const [data, setData] = React.useState([]);

  const { setChangePlan } = React.useContext(ChangePlanContext);

  React.useEffect(() => {
    getChangePlanList().then(setData);
  }, []);

  function onRow(r) {
    const onClick = () => history.push(`/changeplan/${r.id}`);
    return { onClick };
  }

  const footer = () => (
    <div>
      <Button onClick={() => history.push("/changeplan/create")}>
        <PlusOutlined />
      </Button>
    </div>
  );

  async function execute(cpID) {
    await executeChangePlan(cpID);
    setChangePlan(null);
    window.location.reload();
  }

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Change Plans</Typography.Title>
      <CPTable
        rowKey={r => r.id}
        columns={cpColumns(execute)}
        dataSource={data}
        onRow={onRow}
        pagination={false}
        //footer={footer}
          title={footer}
      />
    </div>
  );
}

export default ChangePlanList;
