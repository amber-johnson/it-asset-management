import React from "react";
import { Typography, Table, Input, Pagination } from "antd";
import { getLogs } from "../../../api/log";
import useRedirectOnCPChange from "../../utility/useRedirectOnCPChange";

// a function to create an array of data from a JSON list object based on searchable items
async function createLogArray(username, displayName, identifier, model, page) {
  const { results, count } = await getLogs({
    page,
    page_size: 10, // for now
    username__iexact: username,
    display_name__icontains: displayName,
    model__iexact: model,
    identifier__icontains: identifier,
    ordering: undefined,
    direction: undefined,
  });
  const logList = results;
  console.log("log as list", logList);

  const logLength = Object.keys(logList).length;
  console.log("# log entries", logLength);

  const logArray = [];

  for (let i = 0; i < logLength; i++) {
    const obj = logList[i];

    logArray.push({
      key: i + 1,
      id: obj.id,
      action: obj.action,
      username: obj.username,
      display_name: obj.display_name,
      model: obj.model,
      instance_id: obj.instance_id,
      identifier: obj.identifier,
      field_changed: obj.field_changed,
      old_value: obj.old_value,
      new_value: obj.new_value,
      timestamp: obj.timestamp,
    });
  }

  return {
    total: count,
    data: logArray,
  };
}

// log table headers
const columns = [
  {
    title: "Timestamp",
    dataIndex: "timestamp",
    key: "timestamp",
  },
  {
    title: "Action",
    dataIndex: "action",
    key: "action",
  },
  {
    title: "Username",
    dataIndex: "username",
    key: "username",
  },
  {
    title: "Display Name",
    dataIndex: "display_name",
    key: "display_name",
  },
  {
    title: "Model",
    dataIndex: "model",
    key: "model",
  },
  {
    title: "Identifier",
    dataIndex: "identifier",
    key: "identifier",
    render: (text, record) =>
      MAPPING[record.model] ? (
        <a href={`/#/${MAPPING[record.model]}/${record.instance_id}`}>{text}</a>
      ) : (
        text
      ),
  },
  {
    title: "Field Changed",
    dataIndex: "field_changed",
    key: "field_changed",
  },
  {
    title: "Old Value",
    dataIndex: "old_value",
    key: "old_value",
  },
  {
    title: "New Value",
    dataIndex: "new_value",
    key: "new_value",
  },
];

const MAPPING = {
  ITModel: "models",
  Asset: "assets",
};

function LogManagementPageWrapper() {
  useRedirectOnCPChange();
  return <LogManagementPage />;
}

// a class to build a table searchable by column
class LogManagementPage extends React.Component {
  state = {
    username: "",
    displayName: "",
    identifier: "",
    model: "",
    total: 0,
    page: 1,
    datasource: [],
  };

  componentDidMount() {
    createLogArray(
      this.state.username,
      this.state.displayName,
      this.state.identifier,
      this.state.model,
      this.state.page,
    ).then(({ data, total }) => this.setState({ datasource: data, total }));
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (
      !(
        this.state.page === prevState.page &&
        prevState.username === this.state.username &&
        prevState.displayName === this.state.displayName &&
        prevState.identifier === this.state.identifier &&
        prevState.model === this.state.model
      )
    ) {
      if (this.state.page === prevState.page) {
        createLogArray(
          this.state.username,
          this.state.displayName,
          this.state.identifier,
          this.state.model,
          1,
        ).then(({ data, total }) =>
          this.setState({
            datasource: data,
            total,
            page: 1,
          }),
        );
      } else {
        createLogArray(
          this.state.username,
          this.state.displayName,
          this.state.identifier,
          this.state.model,
          this.state.page,
        ).then(({ data, total }) => this.setState({ datasource: data, total }));
      }
    }
  }

  render() {
    return (
      <div style={{ padding: 16 }}>
        <Typography.Title level={3}>Logs</Typography.Title>

        <Input
          placeholder="Search exact username"
          value={this.state.username}
          onChange={e => this.setState({ username: e.target.value })}
          allowClear
        />

        <Input
          placeholder="Search display name"
          value={this.state.displayName}
          onChange={e => this.setState({ displayName: e.target.value })}
          allowClear
        />

        <Input
          placeholder="Search exact model"
          value={this.state.model}
          onChange={e => this.setState({ model: e.target.value })}
          allowClear
        />

        <Input
          placeholder="Search identifier"
          value={this.state.identifier}
          onChange={e => this.setState({ identifier: e.target.value })}
          allowClear
        />

        <div>
          <Table
            columns={columns}
            dataSource={this.state.datasource}
            pagination={false}
          />
          ;
        </div>
        <Pagination
          page={this.state.page}
          total={this.state.total}
          pageSize={10}
          onChange={(page, pageSize) => {
            this.setState({ page });
          }}
        />
      </div>
    );
  }
}

export default LogManagementPageWrapper;
