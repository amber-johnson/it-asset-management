import React from "react";
import styled from "styled-components";
import { Table, Pagination } from "antd";
import { useHistory } from "react-router-dom";
import DecommissionFilters from "./DecommissionFilters";
import { getDecommissionedAssetList } from "../../../../api/asset";
import { SiteContext } from "../../../../contexts/contexts";
import useRedirectOnCPChange from "../../../utility/useRedirectOnCPChange";

const DecommissionTable = styled(Table)`
  :hover {
    cursor: pointer;
  }
`;

export const decommissionColumns = [
  {
    title: "Model",
    dataIndex: "itmodel",
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
  {
    title: "Host",
    dataIndex: "hostname",
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
  {
    title: "Location",
    dataIndex: "location",
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
  {
    title: "Decommissioned By",
    dataIndex: "decommissioned_by",
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
  {
    title: "Decommissoned At",
    dataIndex: "decommissioned_timestamp",
    sorter: true,
    sortDirections: ["ascend", "descend"],
  },
];

const initialFilterValues = {
  search: "",
  decommissioned_by: "",
  time_from: undefined,
  time_to: undefined,
};

// modelID?: number
function DecommissionList({ modelID }) {
  const history = useHistory();

  const { site } = React.useContext(SiteContext);
  console.log("site from decommisionlist", site);

  const [filterValues, setFilterValues] = React.useState(initialFilterValues);
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(10);
  const [total, setTotal] = React.useState(0);
  const [data, setData] = React.useState([]);
  const [ordering, setOrdering] = React.useState(undefined);
  const [direction, setDirection] = React.useState(undefined);

  const realm = React.useRef(0);

  useRedirectOnCPChange();

  React.useEffect(() => {
    realm.current++;
    const t = realm.current;

    getDecommissionedAssetList({
      search: filterValues.search,
      page,
      page_size: pageSize,
      itmodel: modelID,
      timestamp_from: filterValues.time_from,
      timestamp_to: filterValues.time_to,
      decommissioned_by: filterValues.decommissioned_by,
      decommissioned_timestamp: filterValues.decommissioned_timestamp,
      ordering,
      direction,
      t,
    }).then(r => {
      if (t === realm.current) {
        setData(r.results);
        setTotal(r.count);
      }
    });
  }, [filterValues, page, pageSize, ordering, direction, site?.id]);

  React.useEffect(() => {
    setPage(1);
  }, [filterValues, ordering, direction]);

  const paginationConfig = {
    position: "top",
    total,
    pageSize,
    current: page,
    onChange: (page, pageSize) => {
      setPage(page);
      setPageSize(pageSize);
    },
  };

  function onChange(p, f, sorters) {
    const { column, order } = sorters;
    if (order) {
      setDirection(
        order === "ascend"
          ? "ascending"
          : order === "descend"
          ? "descending"
          : undefined,
      );
      setOrdering(column.dataIndex);
    } else {
      setOrdering(undefined);
    }
  }

  function onRow(r) {
    const onClick = () => history.push(`/assets/readonly/${r.id}`);
    return { onClick };
  }

  return (
    <>
      {modelID == null && (
        <DecommissionFilters
          initialFilterValues={initialFilterValues}
          onChange={setFilterValues}
        />
      )}
      <Pagination {...paginationConfig} style={{ margin: "8px 0" }} />
      <DecommissionTable
        rowKey={r => r.id}
        columns={decommissionColumns}
        dataSource={data}
        onRow={onRow}
        onChange={onChange}
        pagination={false}
      />
    </>
  );
}

export default DecommissionList;
