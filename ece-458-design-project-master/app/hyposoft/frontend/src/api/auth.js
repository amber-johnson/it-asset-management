import Axios from "axios";
import { getData, withLoading } from "./utils";

export function getCurrentUser() {
  return Axios.get("auth/current_user").then(getData);
}

export function getUserList() {
  return Axios.get("api/users/UserList").then(getData);
}

export function login(username, password) {
  return withLoading(() =>
    Axios.post("auth/login", { username, password }).then(getData),
  );
}

export function logout() {
  return Axios.post("auth/logout").then(getData);
}
