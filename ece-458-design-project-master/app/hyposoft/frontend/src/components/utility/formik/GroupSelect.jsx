import React from "react";
import { Select as $Select } from "antd";
import { useField } from "formik";
import { DisableContext } from "../../../contexts/contexts";

// name: string
// groups: { groupName: string, options: { value: T, text: string }[] }[]
// encode?: (value: T) => string
// decode?: (encoded: string) => T
// onChange?: ()
function GroupSelect({ name, groups, encode, decode, onChange, ...props }) {
  const { disabled } = React.useContext(DisableContext);
  const [{ value }, {}, { setValue, setTouched }] = useField(name);

  function enc(value) {
    const v = value && encode ? encode(value) : value;
    return v ?? null;
  }

  function dec(value) {
    const v = value && decode ? decode(value) : value;
    return v ?? null;
  }

  const multiple = props.mode === "multiple";

  return (
    <$Select
      {...props}
      style={{ width: "100%" }}
      disabled={disabled}
      value={multiple ? value.map(enc) : enc(value)}
      showSearch
      filterOption={(input, option) => {
        return (
          !option.label &&
          option.children.toLowerCase().includes(input.toLowerCase())
        );
      }}
      onChange={s => {
        setTouched();
        if (multiple) {
          setValue(s.map(dec));
          onChange && onChange(s.map(dec));
        } else {
          setValue(dec(s));
          onChange && onChange(dec(s));
        }
      }}
    >
      {groups.map(({ groupName, options }, groupIdx) => (
        <$Select.OptGroup key={groupIdx} label={groupName}>
          {options.map(({ value, text }, idx) => (
            <$Select.Option key={groupIdx.toString() + idx} value={enc(value)}>
              {text}
            </$Select.Option>
          ))}
        </$Select.OptGroup>
      ))}
    </$Select>
  );
}

export default GroupSelect;
