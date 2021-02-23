import React from "react";
import styled from "styled-components";
import { Table, Pagination, Button, message } from "antd";
import { useHistory } from "react-router-dom";
import AssetListFooter from "./AssetListFooter";
import NetworkPowerActionButtons from "../NetworkPowerActionButtons";
import AssetFilters from "./AssetFilters";
import { getAssetList } from "../../../../api/asset";
import { SiteContext } from "../../../../contexts/contexts";
import { exportAssets, exportNetwork } from "../../../../api/bulk";
import VSpace from "../../../utility/VSpace";
import useRedirectOnCPChange from "../../../utility/useRedirectOnCPChange";
import ConfigureUserPermissions from "../../../utility/ConfigurePermissions";

const AssetTable = styled(Table)`
  :hover {
  }
`;

export function assetColumns(origin) {
  return [
    {
      title: "Host",
      dataIndex: "hostname",
      sorter: true,
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "Asset Number",
      dataIndex: "asset_number",
      sorter: true,
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "Model",
      dataIndex: "model",
      sorter: true,
      sortdirections: ["ascend", "descend"],
    },
    {
      title: "Location",
      dataIndex: "location",
      sorter: true,
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "Owner",
      dataIndex: "owner",
      sorter: true,
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "Actions",
      key: "actions",
      sorter: false,
      render: r => {
        return (
          <div>
            <a href={`/#${origin}/${r.id}`} style={{ marginRight: 8 }}>
              Details
            </a>
            {r.power_action_visible && (
              <NetworkPowerActionButtons assetID={r.id} />
            )}
          </div>
        );
      },
    },
  ];
}

const initialFilterValues = {
  search: "",
  rack_from: "A01",
  rack_to: "Z99",
  rack_position: [1, 42],
};

// modelID?: number
function AssetList({ modelID, forOffline }) {
  const history = useHistory();
  const config = ConfigureUserPermissions();
  const doDisplay = config.canAssetCUDD;

  const { site } = React.useContext(SiteContext);

  const [filterValues, setFilterValues] = React.useState(initialFilterValues);
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(100000);
  const [total, setTotal] = React.useState(0);
  const [data, setData] = React.useState([]);
  const [ordering, setOrdering] = React.useState(undefined);
  const [direction, setDirection] = React.useState(undefined);
  const [selectedAssets, setSelectedAssets] = React.useState([]); //holds list of selected assets
  const isLoadingList = React.useRef(false);

  useRedirectOnCPChange();

  const realm = React.useRef(0);

  const assetQuery = {
    search: filterValues.search,
    page,
    page_size: pageSize,
    itmodel: modelID,
    rack_from: forOffline ? null : filterValues.rack_from,
    rack_to: forOffline ? null : filterValues.rack_to,
    rack_position_min: forOffline ? null : filterValues.rack_position[0],
    rack_position_max: forOffline ? null : filterValues.rack_position[1],
    site__offline: forOffline ? "True" : "False",
    ordering,
    direction,
  };

  React.useEffect(() => {
    realm.current++;
    const t = realm.current;

    if (!isLoadingList.current) {
      message.loading("Fetching the assets...");
      isLoadingList.current = true;
    }

    getAssetList(assetQuery).then(r => {
      if (t === realm.current) {
        message.destroy();
        isLoadingList.current = false;
        setData(r.results);
        setTotal(r.count);
      }
    });
  }, [filterValues, page, pageSize, ordering, direction, site?.id]);

  React.useEffect(() => {
    setPage(1);
  }, [filterValues, ordering, direction]);

  //effectively no more pagination
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

  //TODO: test rowSelection
  const rowSelection = {
    selectedAssets,
    selections: [Table.SELECTION_ALL, Table.SELECTION_INVERT],
    onChange: setSelectedAssets,
  };

  function handleAssetExport() {
    exportAssets(assetQuery);
  }

  function handleNetworkExport() {
    exportNetwork(assetQuery);
  }

  return (
    <>
      {modelID == null && (
        <div>
          <AssetFilters
            initialFilterValues={initialFilterValues}
            onChange={setFilterValues}
            forOffline={forOffline}
          />
          <VSpace height="8px" />
          <Button
            onClick={() =>
              history.push(`/import/asset?origin=${history.location.pathname}`)
            }
            style={{ marginRight: 8 }}
          >
            Import Assets
          </Button>
          <Button onClick={handleAssetExport}>Export Assets</Button>
          {!forOffline && (
            <div>
              <VSpace height="8px" />
              <Button
                onClick={() =>
                  history.push(
                    `/import/network?origin=${history.location.pathname}`,
                  )
                }
                style={{ marginRight: 8 }}
              >
                Import Network
              </Button>
              <Button onClick={handleNetworkExport}>Export Network</Button>
              <VSpace height="8px" />
            </div>
          )}
        </div>
      )}

      {doDisplay ?
          <AssetListFooter selectedAssets={selectedAssets} />
          : null}

      <Pagination {...paginationConfig} style={{ margin: "8px 0" }} />

      <AssetTable
        rowSelection={rowSelection}
        rowKey={r => r.id}
        columns={assetColumns(forOffline ? "/offline_assets" : "/assets")}
        dataSource={data}
        onChange={onChange}
        pagination={false}
      />
    </>
  );
}

export default AssetList;
