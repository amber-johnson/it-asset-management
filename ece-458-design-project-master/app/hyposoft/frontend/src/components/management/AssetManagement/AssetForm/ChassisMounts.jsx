import React from "react";
import Select from "../../../utility/formik/Select";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import { getRackList } from "../../../../api/rack";
import { getRackViewData } from "../../../../api/report";
import { useFormikContext } from "formik";

function ChassisMounts({ siteList }) {
  const { values } = useFormikContext();
  const { site, rack } = values.location;

  const [rackList, setRackList] = React.useState([]);
  const [rackViewData, setRackViewData] = React.useState([]);

  React.useEffect(() => {
    if (site) {
      getRackList(site).then(setRackList);
    }
  }, [site]);

  React.useEffect(() => {
    if (rack) {
      console.log(rack);
      getRackViewData([rack]).then(res => {
        setRackViewData(res[rack].assets);
      });
    }
  }, [rack]);

  const siteOptions = siteList
    .filter(({ type }) => type === "datacenter")
    .map(({ id, name }) => {
      return { value: id, text: name };
    });

  const rackOptions = rackList.map(({ id, rack }) => {
    return { value: id, text: rack };
  });

  const chassisList = rackViewData
    .filter(({ model }) => model.type === "chassis")
    .map(({ asset }) => asset);

  const chassisOptions = chassisList.map(({ id, hostname, asset_number }) => {
    return { value: id, text: hostname || asset_number.toString() };
  });

  const slotsTaken = rackViewData
    .filter(
      ({ model, asset }) =>
        model.type === "blade" && asset.id === values.location.asset,
    )
    .map(({ asset }) => asset.location.slot);

  const slotOptions = Array(14)
    .fill(null)
    .map((v, idx) => idx + 1) // slots 1-based?
    .filter(n => !slotsTaken.includes(n))
    .map(n => {
      return { value: n, text: n };
    });

  return (
    <div>
      <ItemWithLabel name="location.site" label="Site">
        <Select name="location.site" options={siteOptions} />
      </ItemWithLabel>
      <ItemWithLabel name="location.rack" label="Rack">
        <Select name="location.rack" options={rackOptions} />
      </ItemWithLabel>
      <ItemWithLabel name="location.asset" label="Chassis">
        <Select
          name="location.asset"
          options={chassisOptions}
          disabled={!values.location.rack}
        />
      </ItemWithLabel>
      <ItemWithLabel name="location.slot" label="Available slots">
        <Select
          name="location.slot"
          options={slotOptions}
          disabled={!values.location.asset}
        />
      </ItemWithLabel>
    </div>
  );
}

export default ChassisMounts;
