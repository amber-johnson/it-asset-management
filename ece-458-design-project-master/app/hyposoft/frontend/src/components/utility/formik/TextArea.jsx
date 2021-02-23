import React from "react";
import { Field } from "formik";
import { Input as $Input } from "antd";
import { DisableContext } from "../../../contexts/contexts";

function TextArea({ name, validate, ...props }) {
  const { disabled } = React.useContext(DisableContext);

  return (
    <Field name={name} validate={validate}>
      {({ field: { value }, form: { setFieldValue, setFieldTouched } }) => {
        return (
          <$Input.TextArea
            {...props}
            disabled={disabled}
            value={value}
            onChange={e => {
              const value = e.target.value;
              setFieldValue(name, value);
              setFieldTouched(name, true, false);
            }}
          />
        );
      }}
    </Field>
  );
}

export default TextArea;
