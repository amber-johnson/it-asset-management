import Axios from "axios";
import { makeHeaders, getData } from "./utils";

export function getRackUsage() {
  return Axios.get(`api/equipment/report`, {
    headers: makeHeaders(),
  }).then(getData);
}

export function getRackViewData(rackIDs) {
  return Axios.post(`api/equipment/rack_view`, {
    rack_ids: rackIDs,
  }).then(getData);
}
