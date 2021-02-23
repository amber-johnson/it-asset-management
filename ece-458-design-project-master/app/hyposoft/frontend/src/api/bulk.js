import Axios from "axios";
import jfd from "js-file-download";
import {
  getData,
  makeQueryString,
  processModelQuery,
  processAssetQuery,
} from "./utils";

export function importModels(formData, force) {
  return Axios.post(
    `api/import/ITModel?${makeQueryString({
      force: force,
    })}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  ).then(getData);
}

export function exportModels(query) {
  return Axios.get(
    `api/export/ITModel.csv?${makeQueryString(processModelQuery(query))}`,
  )
    .then(getData)
    .then(data => jfd(data, "models.csv"));
}

export function importAssets(formData, force) {
  return Axios.post(
    `api/import/Asset?${makeQueryString({
      force: force,
    })}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  ).then(getData);
}

export function exportAssets(query) {
  return Axios.get(
    `api/export/Asset.csv?${makeQueryString(processAssetQuery(query))}`,
  )
    .then(getData)
    .then(data => jfd(data, "assets.csv"));
}

export function importNetwork(formData, force) {
  return Axios.post(
    `api/import/Network?${makeQueryString({
      force: force,
    })}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  ).then(getData);
}

export function exportNetwork(query) {
  return Axios.get(
    `api/export/Network.csv?${makeQueryString(processAssetQuery(query))}`,
  )
    .then(getData)
    .then(data => jfd(data, "networks.csv"));
}
