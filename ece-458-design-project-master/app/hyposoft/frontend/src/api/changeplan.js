import Axios from "axios";
import { getData, withLoading } from "./utils";

export function getChangePlanList() {
  return Axios.get("api/changeplan/ChangePlanList").then(getData);
}

export function getChangePlanDetail(id) {
  return Axios.get(`api/changeplan/ChangePlanDetails/${id}`).then(getData);
}

export function getChangePlanActions(id) {
  return Axios.get(`api/changeplan/ChangePlanActions/${id}`).then(getData);
}

export function createChangePlan(name) {
  return withLoading(() =>
    Axios.post(`api/changeplan/ChangePlanCreate`, {
      name,
    }).then(getData),
  );
}

export function executeChangePlan(id) {
  return withLoading(() =>
    Axios.post(`api/changeplan/ChangePlanExecute/${id}`).then(getData),
  );
}

export function updateChangePlan(id, name) {
  return withLoading(() =>
    Axios.patch(`api/changeplan/ChangePlanUpdate/${id}`, {
      name,
    }).then(getData),
  );
}

export function deleteChangePlan(id) {
  return withLoading(() =>
    Axios.delete(`api/changeplan/ChangePlanDestroy/${id}`).then(getData),
  );
}
