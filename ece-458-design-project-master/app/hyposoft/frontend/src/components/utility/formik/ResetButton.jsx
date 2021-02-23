import React from "react";
import { useFormikContext } from "formik";
import { Button } from "antd";
import { DisableContext } from "../../../contexts/contexts";

function ResetButton({ children, ...props }) {
  const { disabled } = React.useContext(DisableContext);
  const { resetForm } = useFormikContext();
  return (
    <Button {...props} disabled={disabled} onClick={resetForm}>
      {children}
    </Button>
  );
}

export default ResetButton;
