import React from "react";
import { Field } from "formik";
import { Input as $Input } from "antd";
import { DisableContext } from "../../../contexts/contexts";

function Input({ name, validate, nullIfBlank, ...props }) {
  const { disabled } = React.useContext(DisableContext);

  return (
    <Field name={name} validate={validate}>
      {({ field: { value }, form: { setFieldValue, setFieldTouched } }) => {
        return (
          <$Input
            {...props}
            value={value}
            disabled={props.disabled || disabled}
            onChange={e => {
              const value = e.target.value;
              setFieldValue(
                name,
                nullIfBlank && value.length == 0 ? null : value,
              );
              setFieldTouched(name, true, false);
            }}
          />
        );
      }}
    </Field>
  );
}

export default Input;
