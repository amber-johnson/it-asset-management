import Axios from "axios";
import { getData, withLoading, makeHeaders } from "./utils";
import {
  indexToRow,
  indexToCol,
} from "../components/management/RackManagement/GridUtils";

export function createRack(siteID, r1, r2, c1, c2) {
  return withLoading(() =>
    Axios.post("api/equipment/RackRangeCreate", {
      site: siteID,
      r1: indexToRow(r1),
      r2: indexToRow(r2),
      c1: indexToCol(c1),
      c2: indexToCol(c2),
    }).then(getData),
  );
}

export function getRackList(siteID) {
  return Axios.get("api/equipment/RackList", {
    headers: makeHeaders({ siteID }),
  }).then(getData);
}

export function deleteRacks(siteID, r1, r2, c1, c2) {
  return withLoading(() =>
    Axios.post(`api/equipment/RackRangeDestroy`, {
      site: siteID,
      r1: indexToRow(r1),
      r2: indexToRow(r2),
      c1: indexToCol(c1),
      c2: indexToCol(c2),
    }).then(getData),
  );
}
