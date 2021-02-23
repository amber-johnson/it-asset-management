import React from "react";
import { Switch as $Switch } from "antd";
import { useField } from "formik";

function Switch({ name }) {
  const [{ value }, {}, { setTouched, setValue }] = useField(name);
  return (
    <$Switch
      checked={value}
      onChange={b => {
        setTouched(true);
        setValue(b);
      }}
    />
  );
}

export default Switch;
