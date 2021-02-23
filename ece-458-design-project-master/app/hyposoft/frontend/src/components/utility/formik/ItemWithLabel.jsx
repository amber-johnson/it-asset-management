import React from "react";
import { Field } from "formik";
import styled from "styled-components";

const BlockSpan = styled("span")`
  display: block;
`;

function ItemWithLabel({ name, label, children, flip, slim, color }) {
  return (
    <div style={{ textAlign: "left", padding: "8px 0", color: "black" }}>
      <BlockSpan style={{ fontWeight: slim ? "normal" : "bold", color }}>
        {label}
      </BlockSpan>
      {!flip && children}
      <Field name={name}>
        {({ meta: { initialError, error, touched } }) => {
          const e = initialError ?? error;
          const displayError = typeof e === "string" && touched;
          const style = {
            visibility: displayError ? "visible" : "hidden",
            color: initialError ? "orange" : "red",
          };
          return (
            <BlockSpan style={style}>
              {displayError ? e : "hidden text"}
            </BlockSpan>
          );
        }}
      </Field>
      {flip && children}
    </div>
  );
}

export default ItemWithLabel;
