import Axios from "axios";
import { getData, makeQueryString } from "./utils";

export function getLogs(query) {
  return Axios.get(
    `api/log/EntryList?${makeQueryString(query)}`,
  ).then(getData);
}
