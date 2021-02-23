import React from "react";
import { Typography, Button, Table } from "antd";
import { getUsers } from "../../../api/user";
import PlusOutlined from "@ant-design/icons/PlusOutlined";
import { useHistory } from "react-router-dom";

const columns = [
  {
    title: "Username",
    dataIndex: "username",
    sorter: false,
  },
  {
    title: "First name",
    dataIndex: "first_name",
    sorter: false,
  },
  {
    title: "Last name",
    dataIndex: "last_name",
    sorter: false,
  },
  {
    title: "Email",
    dataIndex: "email",
    sorter: false,
  },
];

function UserManagementPage() {
  const history = useHistory();

  const [data, setData] = React.useState([]);

  React.useEffect(() => {
    getUsers().then(setData);
  }, []);

  function onRow(r) {
    const onClick = () => history.push(`/users/${r.id}`);
    return { onClick };
  }

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Users</Typography.Title>
      <Table
        onRow={onRow}
        rowKey={r => r.id}
        columns={columns}
        dataSource={data}
        pagination={false}
        title={() => (
          <Button
            onClick={() => {
              history.push("/users/create");
            }}
          >
            <PlusOutlined />
          </Button>
        )}
      />
    </div>
  );
}

export default UserManagementPage;
