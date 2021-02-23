import React from "react";
import { Field } from "formik";
import { AutoComplete as $AutoComplete } from "antd";
import { DisableContext } from "../../../contexts/contexts";

// acList: string[]
function AutoComplete({ name, validate, acList, ...props }) {
  const { disabled } = React.useContext(DisableContext);

  return (
    <Field name={name} validate={validate}>
      {({ field: { value }, form: { setFieldValue, setFieldTouched } }) => {
        const options = acList
          ? acList.filter(ac => ac.toLowerCase().includes(value.toLowerCase()))
          : [];

        return (
          <$AutoComplete
            {...props}
            disabled={disabled}
            value={value}
            style={{ width: "100%" }}
            onChange={value => {
              setFieldValue(name, value);
              setFieldTouched(name, true, false);
            }}
          >
            {options.map((opt, idx) => (
              <$AutoComplete.Option key={idx} value={opt}>
                {opt}
              </$AutoComplete.Option>
            ))}
          </$AutoComplete>
        );
      }}
    </Field>
  );
}

export default AutoComplete;
