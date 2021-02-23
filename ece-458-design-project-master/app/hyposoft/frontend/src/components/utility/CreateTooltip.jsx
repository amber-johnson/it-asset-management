import React from "react";
import { Tooltip } from "antd";

function CreateTooltip({ isVisible, tooltipText, children }) {
  const ret = isVisible ? (
    <Tooltip placement="right" title={tooltipText}>
      {children}
    </Tooltip>
  ) : (
    children
  );

  //console.log(isVisible, ret);
  return ret;
}

export default CreateTooltip;
