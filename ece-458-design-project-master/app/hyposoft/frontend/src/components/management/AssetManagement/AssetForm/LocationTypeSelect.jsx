import React from "react";
import { useField, useFormikContext } from "formik";
import { DisableContext } from "../../../../contexts/contexts";
import { Radio } from "antd";

function LocationSelect({ model, locked, ...restProps }) {
  const { disabled } = React.useContext(DisableContext);
  const { setFieldValue, values } = useFormikContext();
  const [{ value }, {}, { setValue, setTouched }] = useField("location.tag");

  React.useEffect(() => {
    if (model && !locked.current) {
      const type = model.type;

      if (type !== "blade" && values.location.tag === "chassis-mount") {
        setFieldValue("location.tag", "rack-mount");
      } else if (type === "blade" && values.location.tag === "rack-mount") {
        setFieldValue("location.tag", "chassis-mount");
      }

      if (type !== "blade") {
        setFieldValue(
          "network_ports",
          model.network_port_labels.map(label => {
            return {
              label,
              mac_address: null,
              connection: null,
            };
          }),
          false,
        );
        setFieldValue("power_connections", [], false);
      } else {
        setFieldValue("network_ports", [], false);
        setFieldValue("power_connections", [], false);
      }
    }
  }, [model]);

  React.useEffect(() => {
    if (value && !locked.current) {
      let empty = null;

      switch (value) {
        case "rack-mount":
          empty = {
            tag: value,
            site: null,
            rack: null,
            rack_position: null,
          };
          break;
        case "chassis-mount":
          empty = {
            tag: value,
            site: null,
            rack: null,
            asset: null,
            slot: null,
          };
          break;
        case "offline":
          empty = {
            tag: value,
            site: null,
          };
      }

      if (empty) {
        setFieldValue("location", empty);
      }
    }
  }, [value]);

  function onChange(e) {
    setTouched(true);
    setValue(e.target.value);
  }

  const rackMountDisabled = model?.type === "blade";
  const chassisMountDisabled = model?.type !== "blade";

  return (
    <Radio.Group
      onChange={onChange}
      value={value}
      disabled={disabled}
      {...restProps}
    >
      <Radio value="rack-mount" disabled={rackMountDisabled}>
        Rack Mount
      </Radio>
      <Radio value="chassis-mount" disabled={chassisMountDisabled}>
        Chassis Mount
      </Radio>
      <Radio value="offline">Offline</Radio>
    </Radio.Group>
  );
}

export default LocationSelect;
