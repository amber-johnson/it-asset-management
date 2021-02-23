import React from "react";
import { getAsset } from "../../../api/asset";
import { getRackViewData } from "../../../api/report";
import { Typography, Alert } from "antd";
import { useHistory } from "react-router-dom";
import s from "./ChassisView.module.css";

// provide either of these two
function ChassisView({ assetID }) {
  const [isInOffline, setIsInOffline] = React.useState(false);
  const [chassis, setChassis] = React.useState(null);
  const [blades, setBlades] = React.useState([]);

  React.useEffect(() => {
    if (assetID) {
      (async () => {
        const asset = await getAsset(assetID);
        const rack = asset?.location.rack;
        if (rack) {
          const rackViewData = (await getRackViewData([rack]))[rack].assets;

          const chassis = rackViewData.find(
            ({ model, asset: a }) =>
              model.type === "chassis" &&
              (a.id === asset.id || a.id === asset.location.asset),
          );

          const blades = rackViewData.filter(
            ({ model, asset: a }) =>
              model.type === "blade" && a.location.asset === chassis?.asset.id,
          );

          setChassis(chassis);
          setBlades(blades);
        } else {
          setIsInOffline(!rack);
        }
      })();
    }
  }, [assetID]);

  return (
    <div>
      <Typography.Title level={4}>Chassis View</Typography.Title>
      {isInOffline ? (
        <Alert
          message="This asset is in offline storage"
          type="info"
          showIcon
        />
      ) : chassis ? (
        <table>
          <thead>
            <tr>
              <th
                colSpan={14}
                style={{
                  backgroundColor:
                    chassis.asset.display_color || chassis.model.display_color,
                  border: "1pt black solid",
                  color: "white",
                  textShadow:
                    "0.05em 0 black, 0 0.05em black, -0.05em 0 black, 0 -0.05em black, -0.05em -0.05em black, -0.05em 0.05em black, 0.05em -0.05em black, 0.05em 0.05em black",
                  textAlign: "center",
                }}
                className={s.clickable}
                onClick={() => {
                  window.location.href = `/#/assets/${chassis.asset.id}`;
                  window.location.reload();
                }}
              >
                {`${chassis.asset.id == assetID ? "*" : ""} Chassis (${chassis
                  .asset.hostname || chassis.asset.asset_number})`}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              {Array(14)
                .fill(null)
                .map((v, idx) => {
                  const blade = blades.find(
                    ({ asset }) => asset.location.slot === idx + 1,
                  );
                  if (blade) {
                    const { model, asset } = blade;
                    return (
                      <td
                        key={idx}
                        style={{
                          backgroundColor:
                            asset.display_color || model.display_color,
                          border: "1pt black solid",
                          color: "white",
                          textShadow:
                            "0.05em 0 black, 0 0.05em black, -0.05em 0 black, 0 -0.05em black, -0.05em -0.05em black, -0.05em 0.05em black, 0.05em -0.05em black, 0.05em 0.05em black",
                          minWidth: 20,
                          height: 20,
                          textAlign: "center",
                        }}
                        onClick={() => {
                          window.location.href = `/#/assets/${asset.id}`;
                          window.location.reload();
                        }}
                        className={s.clickable}
                      >
                        {`${idx} ${asset.id == assetID ? "*" : ""}`}
                      </td>
                    );
                  } else {
                    return (
                      <td
                        key={idx}
                        style={{
                          border: "1pt black solid",
                          textShadow: "white 0px 0px 10px",
                          minWidth: 20,
                          height: 20,
                        }}
                      />
                    );
                  }
                })}
            </tr>
          </tbody>
        </table>
      ) : (
        <Alert message="This asset is a regular mount" type="info" showIcon />
      )}
    </div>
  );
}

export default ChassisView;
