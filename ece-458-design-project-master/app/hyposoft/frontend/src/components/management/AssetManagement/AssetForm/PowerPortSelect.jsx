import React from "react";
import Select from "../../../utility/formik/Select";
import VSpace from "../../../utility/VSpace";
import Input from "../../../utility/formik/Input";
import styled from "styled-components";

const BlockHeader = styled("h4")`
  margin: 0;
`;

const BlockText = styled("p")`
  margin: 0;
`;

function PowerPortSelect({ powerPorts, total }) {
  const name = "power_connections";

  console.log("power ports are ", powerPorts);
  console.log("num ports is ", total);
  const nums = [
    ...Array(total)
      .fill(null)
      .keys(),
  ];

  return (
    /*<Select
      name={name}
      mode="multiple"
      options={powerPorts.map(({ pdu_id, plug, label }) => {
        return {
          value: { pdu_id, plug },
          text: label,
        };
      })}
      encode={({ pdu_id, plug }) => `${pdu_id},${plug}`}
      decode={s => {
        const [pdu_id, plug] = s.split(",");
        return { pdu_id, plug };
      }}
    />*/
    //powerPorts.map((pdu_id, plug, label) => <Select>Hi</Select>)
    <div>
      {nums.map((val, index) => (
        <div key={index}>
          <VSpace height="8px" />
          <BlockHeader>Power Plug {val + 1}</BlockHeader>
          <Select
            name={name + "." + index}
            options={powerPorts.map(({ pdu_id, plug, label }) => {
              return {
                value: { pdu_id, plug },
                text: label,
              };
            })}
            encode={({ pdu_id, plug }) => `${pdu_id},${plug}`}
            decode={s => {
              const [pdu_id, plug] = s.split(",");
              return { pdu_id, plug };
            }}
            allowClear
          />
        </div>
      ))}
    </div>
  );
}

export default PowerPortSelect;
