import React from "react";
import Select from "../../../utility/formik/Select";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import { getRackList } from "../../../../api/rack";
import InputNumber from "../../../utility/formik/InputNumber";
import { powerPortList } from "../../../../api/power";
import NetworkPortSelect from "./NetworkPortSelect";
import PowerPortSelect from "./PowerPortSelect";
import { useFormikContext } from "formik";

function RackMounts({ model, siteList }) {
  const { values, setFieldValue } = useFormikContext();
  const { site, rack } = values.location;

  const [rackList, setRackList] = React.useState([]);
  const [powerPorts, setPowerPorts] = React.useState([]);

  React.useEffect(() => {
    if (site) {
      getRackList(site).then(setRackList);
    }
  }, [site]);

  React.useEffect(() => {
    if (rack) {
      powerPortList(rack).then(setPowerPorts);
    }
  }, [rack]);

  const siteOptions = siteList
    .filter(({ type }) => type === "datacenter")
    .map(({ id, name }) => {
      return { value: id, text: name };
    });

  const rackOptions = rackList.map(({ id, rack }) => {
    return { value: id, text: rack };
  });

  return (
    <div>
      <ItemWithLabel name="location.site" label="Site">
        <Select name="location.site" options={siteOptions} />
      </ItemWithLabel>
      <ItemWithLabel name="location.rack" label="Rack">
        <Select
          name="location.rack"
          options={rackOptions}
          onChange={() => {
            setFieldValue("power_connections", [], false);
          }}
        />
      </ItemWithLabel>
      <ItemWithLabel name="location.rack_position" label="Rack Position">
        <InputNumber name="location.rack_position" min={1} max={42} />
      </ItemWithLabel>
      <ItemWithLabel name="power_connections" label="Power connections">
        <PowerPortSelect powerPorts={powerPorts} total={model?.power_ports} />
      </ItemWithLabel>
      <ItemWithLabel name="network_ports" label="Network ports" flip>
        <NetworkPortSelect selectedModel={model} />
      </ItemWithLabel>
    </div>
  );
}

export default RackMounts;
