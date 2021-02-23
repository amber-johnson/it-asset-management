import React from "react";
import { useField } from "formik";
import { ChromePicker } from "react-color";
import { DisableContext } from "../../../../contexts/contexts";
import { Checkbox } from "antd";

function ColorPicker({ name, nullable, placeholder, ...restProps }) {
  const { disabled } = React.useContext(DisableContext);
  const [{ value }, {}, { setValue }] = useField(name);

  function handleChange(e) {
    if (e.target.checked) {
      setValue("#0ff");
    } else {
      setValue(null);
    }
  }

  return (
    <div>
      {nullable && (
        <div>
          Use upgrade{" "}
          <Checkbox checked={value != null} onChange={handleChange} />
        </div>
      )}
      <ChromePicker
        disableAlpha
        color={value ?? placeholder}
        onChange={color => {
          if (disabled || value == null) return;
          setValue(color.hex);
        }}
        {...restProps}
      />
    </div>
  );
}

export default ColorPicker;
