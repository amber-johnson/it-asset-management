import Axios from "axios";
import { getData, withLoading } from "./utils";

export function createSite(fields) {
  return withLoading(() =>
    Axios.post("api/equipment/SiteCreate", fields).then(getData),
  );
}

export function getSites() {
  return Axios.get(`api/equipment/SiteList`).then(getData);
}

export function updateSite(id, updates) {
  return withLoading(() =>
    Axios.patch(`api/equipment/SiteUpdate/${id}`, updates).then(getData),
  );
}

export function deleteSite(id) {
  return withLoading(() =>
    Axios.delete(`api/equipment/SiteDestroy/${id}`).then(getData),
  );
}
