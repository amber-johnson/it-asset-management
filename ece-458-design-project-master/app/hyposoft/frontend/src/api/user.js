import { withLoading, getData } from "./utils";
import Axios from "axios";

export function createUser(fields) {
  return withLoading(() =>
    Axios.post("auth/UserCreate", {
      user: fields,
      password: fields.password,
    }).then(getData),
  );
}

export function getUser(id) {
  return Axios.get(`auth/UserRetrieve/${id}`).then(getData);
}

export function getUsers() {
  return Axios.get("auth/UserList").then(getData);
}

export function updateUser(id, updates) {
  return Axios.patch(`auth/UserUpdate/${id}`, updates).then(getData);
}

export function deleteUser(id) {
  return Axios.delete(`auth/UserDestroy/${id}`).then(getData);
}
