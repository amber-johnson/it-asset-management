import React from "react";
import { Typography, Divider, Row, Col } from "antd";
import styled from "styled-components";
import { getAssetDetail } from "../../../../api/asset";
import { useParams } from "react-router-dom";
import VSpace from "../../../utility/VSpace";
import NetworkGraph from "../../AssetManagement/AssetForm/NetworkGraph";
import useRedirectOnCPChange from "../../../utility/useRedirectOnCPChange";

const Label = styled("span")`
  display: block;
  font-weight: bold;
  font-size: 14pt;
`;

const Value = styled("span")`
  display: block;
  font-size: 12pt;
`;

function AssetDetailView() {
  const { id } = useParams();

  const [asset, setAsset] = React.useState(null);

  React.useEffect(() => {
    getAssetDetail(id).then(setAsset);
  }, [id]);

  useRedirectOnCPChange("/decommission");

  if (!asset) return null;

  const {
    asset_number,
    hostname,
    itmodel,
    display_color,
    storage,
    memory,
    cpu,
    location,
    decommissioned,
    decommissioned_by,
    decommissioned_timestamp,
    power_connections,
    network_ports,
    network_graph,
    comment,
    owner,
  } = asset;

  const { vendor, model_number, type } = itmodel;
  const { tag, site } = location;
  const powerConnStr = (power_connections ?? [])
    .map(({ label }) => label)
    .join(", ");

  const networkPorts = network_ports ?? [];
  const networkPortView =
    networkPorts.length > 0
      ? networkPorts.map(({ label, mac_address, connection_str }, idx) => (
          <div key={idx}>
            <div
              style={{
                display: "inline-block",
                border: "1pt solid #eee",
                padding: 8,
              }}
            >
              <Label>{label}</Label>
              <VSpace height="8px" />

              <Label>MAC Address</Label>
              <Value>{mac_address ?? "(empty)"}</Value>
              <VSpace height="8px" />

              <Label>Connected To</Label>
              <Value>{connection_str ?? "(empty)"}</Value>
            </div>
            <VSpace height="8px" />
          </div>
        ))
      : "(empty)";

  return (
    <Row style={{ padding: 16 }}>
      <Col md={8}>
        <Typography.Title level={4}>Asset Details</Typography.Title>
        <Label>Asset #</Label>
        <Value>{asset_number}</Value>
        <VSpace height="8px" />

        <Label>Hostname</Label>
        <Value>{hostname}</Value>
        <VSpace height="8px" />

        <Label>Model</Label>
        <Value>{`${model_number} by ${vendor}`}</Value>
        <VSpace height="8px" />

        <Divider>Upgrades</Divider>
        <p>* Upgraded values are indicated in orange</p>

        <Label style={display_color && { color: "orange" }}>
          Display_color
        </Label>
        <div
          style={{
            width: 20,
            height: 20,
            backgroundColor: display_color ?? itmodel.display_color,
          }}
        />
        <VSpace height="8px" />

        <Label style={storage && { color: "orange" }}>Storage</Label>
        <Value>{`${(storage ?? itmodel.storage) || "(empty)"}`}</Value>
        <VSpace height="8px" />

        <Label style={memory && { color: "orange" }}>Memory</Label>
        <Value>{`${(memory ?? itmodel.memory) || "(empty)"}`}</Value>
        <VSpace height="8px" />

        <Label style={cpu && { color: "orange" }}>CPU</Label>
        <Value>{`${(cpu ?? itmodel.cpu) || "(empty)"}`}</Value>
        <VSpace height="8px" />

        <Divider />

        <Label>Location</Label>
        {tag === "rack-mount" ? (
          <Value>{`${location.site.abbr} ${location.rack.rack} U${location.rack_position}`}</Value>
        ) : tag === "chassis-mount" ? (
          <Value>{`${location.site.abbr} ${location.asset_hostname ?? ""} #${
            location.asset.asset_number
          } SLOT ${location.slot}`}</Value>
        ) : tag === "offline" ? (
          <Value>{`${location.site.abbr}`}</Value>
        ) : null}
        <VSpace height="8px" />

        {decommissioned && (
          <div>
            <Label>Decommissioned By</Label>
            <Value>{decommissioned_by.username}</Value>
            <VSpace height="8px" />

            <Label>Decommissioned At</Label>
            <Value>{decommissioned_timestamp}</Value>
            <VSpace height="8px" />
          </div>
        )}

        {type !== "blade" ? (
          <div>
            <Label>Power connections</Label>
            <Value>{powerConnStr || "(empty)"}</Value>
            <VSpace height="8px" />

            <Label>Network Ports</Label>
            {networkPortView}
            <VSpace height="8px" />
          </div>
        ) : null}

        <Label>Owner</Label>
        <Value>{owner?.username ?? "(empty)"}</Value>
        <VSpace height="8px" />

        <Label>Comment</Label>
        <pre>{comment || "(empty)"}</pre>
        <VSpace height="8px" />

        <Divider />

        <Label>Network Graph</Label>
        <NetworkGraph assetID={id} networkGraph={network_graph} />
        <VSpace height="8px" />
      </Col>
    </Row>
  );
}

export default AssetDetailView;
