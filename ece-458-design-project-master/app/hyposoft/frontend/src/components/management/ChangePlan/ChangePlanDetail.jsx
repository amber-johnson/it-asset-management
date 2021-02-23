import React, { useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { Typography, Button, Divider, Input } from "antd";
import {
  executeChangePlan,
  updateChangePlan,
  getChangePlanDetail,
} from "../../../api/changeplan";
import Diff from "../../utility/Diff";
import { ChangePlanContext } from "../../../contexts/contexts";

const ASSET_HEADERS = [
  {
    name: "asset #",
    toText: ad => ad.asset_number,
  },
  {
    name: "hostname",
    toText: ad => ad.hostname ?? "",
  },
  {
    name: "model",
    toText: ad =>
      (({ vendor, model_number }) => `${model_number} by ${vendor}`)(
        ad.itmodel,
      ),
  },
  {
    name: "location",
    toText: ad => {
      if (ad.location.tag === "rack-mount") {
        return `${ad.location.site.abbr}: Rack ${ad.location.rack.rack}U${ad.location.rack_position}`;
      } else if (ad.location.tag === "chassis-mount") {
        let chassis_str = ad.location.asset?.hostname;
        if (!chassis_str) {
          chassis_str = ad.location.asset?.asset_number;
          if (!chassis_str)
            chassis_str = "ID #" + ad.location.asset.id.toString();
          else chassis_str = "#" + chassis_str;
        }
        return `${ad.location.site.abbr}: ${"Rack " + ad.location.rack?.rack ??
          ""} Chassis ${chassis_str} Slot ${ad.location.slot.toString()}`;
      } else if (ad.location.tag === "offline") {
        return ad.location.site.name;
      }
    },
  },
  {
    name: "power conn.",
    toText: ad =>
      (ad.power_connections ?? [])
        .map(({ label }) => label)
        .sort()
        .join("\n"),
  },
  {
    name: "network conn.",
    toText: ad =>
      (ad.network_ports ?? [])
        .map(
          ({ label, connection_str }) =>
            `${label} -> ${connection_str ?? "(Nothing)"}`,
        )
        .join("\n"),
  },
  {
    name: "comment",
    toText: ad => ad.comment ?? "",
  },
  {
    name: "owner",
    toText: ad => ad.owner?.username ?? "",
  },
  {
    name: "upgrade color",
    toText: ad => ad.display_color ?? "",
  },
  {
    name: "upgrade memory",
    toText: ad => ad.memory ?? "",
  },
  {
    name: "upgrade storage",
    toText: ad => ad.storage ?? "",
  },
  {
    name: "upgrade cpu",
    toText: ad => ad.cpu ?? "",
  },
  {
    name: "decommissioned by",
    toText: ad => {
      return ad.decommissioned_by?.username ?? "N/A"},
  },
];

function ChangePlanDetail() {
  const { id } = useParams();

  const history = useHistory();

  const { setChangePlan: setGlobalChangePlan, refresh } = React.useContext(
    ChangePlanContext,
  );

  const [changePlan, setChangePlan] = React.useState(null);
  const [conflicted, setConflicted] = React.useState(false);

  React.useEffect(() => {
    getChangePlanDetail(id).then(cp => {
      setChangePlan(cp);
      setConflicted(false);
      cp.diffs.map(({ conflicts }) => {
        if (conflicts.length > 0) {
          setConflicted(true);
        }
      });
      console.log("change plan from effect", cp);
    });
  }, [id]);

  if (!changePlan) return null;

  function openWorkOrder() {
    window.open("/#/changeplan/workorder?cp_id=" + id);
  }

  async function onUpdate(newName) {
    console.log("updated");
    await updateChangePlan(id, newName);
    const newCP = {
      ...changePlan,
      name: newName,
    };
    setChangePlan(newCP);
    setGlobalChangePlan(newCP);
    refresh();
  }

  async function execute() {
    await executeChangePlan(id);
    setGlobalChangePlan(null);
    history.push("/changeplan");
  }

  const summaryHeaders = ASSET_HEADERS.map(({ name }) => name);

  const summaryDiff = changePlan.diffs.map(({ live, cp, conflicts }) => {

    const before =
      live != null ? ASSET_HEADERS.map(({ toText }) => toText(live)) : null;

    const after =
      cp != null ? ASSET_HEADERS.map(({ toText }) => toText(cp)) : null;

    const error =
      conflicts.length === 0
        ? null
        : conflicts
            .map(({ field, message }) => `${field}: ${message}`)
            .join("\n");

    const action =
      conflicts.length === 0
        ? null
        : {
            name: "Fix it",
            onClick: () => {
              //const id = before.id && after.id;
              setGlobalChangePlan({ id: changePlan.id, name: changePlan.name });
              history.push(`/assets/${cp.id}`);
            },
          };

    return {
      before,
      after,
      error,
      warning: null,
      action,
    };
  });

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={3}>Change Plan Details</Typography.Title>

      <Divider />

      <Typography.Title level={4}>Basic Info</Typography.Title>
      <Typography.Text>Name: </Typography.Text>
      <Typography.Text editable={{ onChange: onUpdate }}>
        {changePlan?.name ?? ""}
      </Typography.Text>
      {changePlan?.executed_at && (
        <Typography.Paragraph style={{ color: "blue" }}>
          Executed on {changePlan?.executed_at}
        </Typography.Paragraph>
      )}

      <Divider />

      <Typography.Title level={4}>Change Summary</Typography.Title>

      {/*<Diff0 messages={summaryDiff0()} />*/}

      <Diff
        headers={summaryHeaders}
        diff={summaryDiff}
        beforeText="Live"
        afterText="Plan"
      />

      <Divider />

      <Button
        type="primary"
        onClick={execute}
        disabled={conflicted || changePlan?.executed_at}
        style={{ marginRight: 16 }}
      >
        Execute
      </Button>
      <Button onClick={openWorkOrder} disabled={conflicted}>
        Work Order
      </Button>
    </div>
  );
}

export default ChangePlanDetail;
