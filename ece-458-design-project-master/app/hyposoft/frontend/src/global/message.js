import { message } from "antd";

const MESSAGE_DURATION = 5;
const MAX_ERROR_MSG_LENGTH = 200;

export function displayInfo(msg) {
  message.info(msg, MESSAGE_DURATION);
}

export function displayWarning(msg) {
  message.warning(msg, MESSAGE_DURATION);
}

export function displayError(msg) {
  console.log(msg);
  let str = msg;
  if (typeof msg === "object") {
    if (Array.isArray(msg)) {
      str = msg.join("\n");
    } else if (msg.message) str = msg.message;
    else
      str = Object.entries(msg)
        .map(([k, v]) => `${k}: ${v}`)
        .join("\n");
  }
  if (str.length > MAX_ERROR_MSG_LENGTH) {
    str = str.substring(0, MAX_ERROR_MSG_LENGTH) + " ...";
  }

  message.error(str, MESSAGE_DURATION);
}
