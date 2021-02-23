import React from "react";
import { useFormikContext } from "formik";

function FormDebugger() {
  const { values, errors, touched } = useFormikContext();
  console.log(values);
  return (
    <div style={{ textAlign: "left" }}>
      <pre>{JSON.stringify(values, null, 2)}</pre>
      <pre>{JSON.stringify(errors, null, 2)}</pre>
      <pre>{JSON.stringify(touched, null, 2)}</pre>
    </div>
  );
}

export default FormDebugger;
