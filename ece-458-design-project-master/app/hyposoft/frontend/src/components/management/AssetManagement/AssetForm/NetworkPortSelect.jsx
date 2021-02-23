import React from "react";
import styled from "styled-components";
import Input from "../../../utility/formik/Input";
import VSpace from "../../../utility/VSpace";
import { useFormikContext } from "formik";
import { networkPortList } from "../../../../api/asset";
import GroupSelect from "../../../utility/formik/GroupSelect";

const BlockHeader = styled("h4")`
  margin: 0;
`;

const BlockText = styled("p")`
  margin: 0;
`;

function NetworkPortSelect({ selectedModel }) {
  return (
    selectedModel &&
    selectedModel.network_port_labels.map((label, idx) => (
      <div key={idx}>
        <VSpace height="8px" />
        <BlockHeader>Label: {label}</BlockHeader>
        <BlockText>MAC address</BlockText>
        <Input name={`network_ports.${idx}.mac_address`} />
        <AssetNetworkPortSelect idx={idx} />
        <VSpace height="8px" />
      </div>
    ))
  );
}

function AssetNetworkPortSelect({ idx }) {
  const { values } = useFormikContext();

  const [networkPorts, setNetworkPorts] = React.useState([]);

  React.useEffect(() => {
    if (values?.location.site) {
      networkPortList().then(setNetworkPorts);
    }
  }, [values?.location.site]);

  const networkPortGroups = Object.entries(
    networkPorts.reduce((acc, np) => {
      acc[np.asset_str] = [...(acc[np.asset_str] ?? []), np];
      return acc;
    }, {}),
  ).reduce((acc, [assetStr, nps]) => {
    acc.push({
      groupName: assetStr,
      options: nps.map(({ id, label }) => {
        return { value: id, text: `${assetStr} > ${label}` };
      }),
    });
    return acc;
  }, []);

  return (
    <div>
      <BlockText>Connection</BlockText>
      <GroupSelect
        allowClear
        name={`network_ports.${idx}.connection`}
        groups={networkPortGroups}
      />
    </div>
  );
}

export default NetworkPortSelect;
