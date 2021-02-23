import React from "react";
import { Button } from "antd";
import useTrigger from "../../utility/useTrigger";
import {
  getPowerState,
  updatePowerState,
  runPowerCycle,
} from "../../../api/power";

function preventing(op, onSuccess) {
  return e => {
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation();
    op(e).then(onSuccess);
  };
}

const ON = "On";
const OFF = "Off";

function NetworkPowerActionButtons({
  assetID,
  displayState,
}) {
  const [trigger, fireTrigger] = useTrigger();
  const [powerState, setPowerState] = React.useState("");

  React.useEffect(() => {
    if (displayState) {
      getPowerState(assetID).then(setPowerState);
    }
  }, [displayState, trigger]);

  return (
    <>
      <Button.Group>
        <Button
          onClick={preventing(
            () => updatePowerState(assetID, "on"),
            fireTrigger,
          )}
          type={
            powerState === ON && displayState
              ? "primary"
              : "default"
          }
        >
          On
        </Button>
        <Button
          onClick={preventing(
            () => updatePowerState(assetID, "off"),
            fireTrigger,
          )}
          type={
            powerState === OFF && displayState
              ? "dashed"
              : "default"
          }
        >
          Off
        </Button>
        <Button
          onClick={preventing(
            () => runPowerCycle(assetID),
            fireTrigger,
          )}
        >
          Cycle
        </Button>
      </Button.Group>
    </>
  );
}

export default NetworkPowerActionButtons;
