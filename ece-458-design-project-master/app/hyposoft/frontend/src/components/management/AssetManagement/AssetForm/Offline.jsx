import React from "react";
import Select from "../../../utility/formik/Select";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";

function Offline({ siteList }) {
  const options = siteList
    .filter(({ type }) => type === "offline-storage")
    .map(({ id, name }) => {
      return { value: id, text: name };
    });

  return (
    <div>
      <ItemWithLabel name="location.site" label="Site">
        <Select name="location.site" options={options} />
      </ItemWithLabel>
    </div>
  );
}

export default Offline;
