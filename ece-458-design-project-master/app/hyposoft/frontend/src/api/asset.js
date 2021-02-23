import Axios from "axios";
import {
  getData,
  makeQueryString,
  makeHeaders,
  withLoading,
  processAssetQuery,
} from "./utils";

export function createAsset(fields) {
  return withLoading(() =>
    Axios.post("api/equipment/AssetCreate", fields, {
      header: makeHeaders(),
    }).then(getData),
  );
}

export async function getAssetList(query) {
  const queryStr = makeQueryString(processAssetQuery(query));

  const resp = await Axios.get(`api/equipment/AssetList?${queryStr}`, {
    headers: makeHeaders(),
  });

  return getData(resp);
}

export function getDecommissionedAssetList(query) {
  return Axios.get(
    `api/equipment/DecommissionedAssetList?${makeQueryString(query)}`,
    { headers: makeHeaders() },
  ).then(getData);
}

export function getAssetPicklist(query) {
  return Axios.get(`api/equipment/AssetPickList?${makeQueryString(query)}`, {
    headers: makeHeaders(),
  }).then(getData);
}

export function decommissionAsset(id) {
  return withLoading(() =>
    Axios.post(`api/equipment/DecommissionAsset/${id}`, null, {
      headers: makeHeaders(),
    }).then(getData),
  );
}

export function getAsset(id) {
  if (id == null) {
    return null;
  }
  return Axios.get(`api/equipment/AssetRetrieve/${id}`, {
    headers: makeHeaders(),
  }).then(getData);
}

export function getAssetDetail(id) {
  return Axios.get(`api/equipment/AssetDetailRetrieve/${id}`, {
    headers: makeHeaders(),
  }).then(getData);
}

export function updateAsset(id, updates) {
  return withLoading(() =>
    Axios.patch(`api/equipment/AssetUpdate/${id}`, updates, {
      headers: makeHeaders(),
    }).then(getData),
  );
}

export function deleteAsset(id) {
  return withLoading(() =>
    Axios.delete(`api/equipment/AssetDestroy/${id}`, {
      headers: makeHeaders(),
    }).then(getData),
  );
}

export function networkPortList(assetID) {
  return Axios.get(
    `api/network/NetworkPortList?${makeQueryString({ asset_id: assetID })}`,
    { headers: makeHeaders() },
  ).then(getData);
}

export function getAssetIDForAssetNumber(assetNumber) {
  return Axios.get(`api/equipment/AssetIDForAssetNumber/${assetNumber}`).then(
    getData,
  );
}
