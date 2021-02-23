import React from "react";
import { useField } from "formik";
import { DisableContext } from "../../../../contexts/contexts";
import { Radio } from "antd";

function TypePicker({ name, ...restProps }) {
  const { disabled } = React.useContext(DisableContext);
  const [{ value }, {}, { setValue, setTouched }] = useField(name);

  function onChange(e) {
    setTouched(true);
    setValue(e.target.value);
  }

  return (
    <Radio.Group
      onChange={onChange}
      value={value}
      disabled={disabled}
      {...restProps}
    >
      <Radio value="regular">Regular</Radio>
      <Radio value="chassis">Chassis</Radio>
      <Radio value="blade">Blade</Radio>
    </Radio.Group>
  );
}

export default TypePicker;
