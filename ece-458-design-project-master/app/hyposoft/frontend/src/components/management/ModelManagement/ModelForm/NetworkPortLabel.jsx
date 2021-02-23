import React from "react";
import { Field, useField } from "formik";
import { InputNumber } from "antd";
import produce from "immer";
import Input from "../../../utility/formik/Input";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import VSpace from "../../../utility/VSpace";
import { DisableContext } from "../../../../contexts/contexts";

function fitNum(arr, num) {
  return produce(arr, draft => {
    if (num < draft.length) {
      draft.splice(num, draft.length - num);
    } else {
      for (let i = draft.length; i < num; i++) {
        draft.push((i + 1).toString());
      }
    }
  });
}

function NetworkPortLabelFormItem({ name }) {
  const { disabled } = React.useContext(DisableContext);
  const [{ value }, {}, { setValue }] = useField(name);

  function handleNumChange(num) {
    setValue(fitNum(value, num));
  }

  return (
    <div>
      <InputNumber
        disabled={disabled}
        value={value.length}
        onChange={handleNumChange}
        min={0}
      />
      <VSpace height={value.length > 0 ? "8px" : "0"} />
      {value.map((v, idx) => {
        const innerName = `${name}.${idx}`;
        return (
          <ItemWithLabel
            name={innerName}
            key={idx}
            label={`Network port label #${idx}`}
            slim
          >
            <Input name={innerName} />
          </ItemWithLabel>
        );
      })}
    </div>
  );
}

export default NetworkPortLabelFormItem;
