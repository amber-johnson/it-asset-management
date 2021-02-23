import React from "react";
import { useFormikContext } from "formik";
import { Button } from "antd";
import { DisableContext } from "../../../contexts/contexts";

function SubmitButton({ children, ...props }) {
  const { disabled } = React.useContext(DisableContext);
  const { submitForm } = useFormikContext();
  return (
    <Button {...props} disabled={disabled} onClick={submitForm}>
      {children}
    </Button>
  );
}

export default SubmitButton;
