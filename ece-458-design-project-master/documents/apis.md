# API specs

## General notes

- This document is never final; Whenever there needs to be changes to the document, feel free to do so.

- There's a difference between `null` and `undefined`.

  `undefined` means that the field might be a string, or not included at all.

  `null` means that the field exists, but just given a null value.

- When the type is `String | null`, treat empty string as `null`.

- The type `XXX_ID` is a foreign key to another model - with a type `int`.

- The type `XXX_STR` is a string that allows an user to distinguish what the object is. It isn't used for any other reason than simply displaying it.

- Most of the APIs, unless stated in its `Notes` section, should be performed in a transactionsal manner - change application state only on success.

  On success, return whatever that's in the `Response Body`.

  On error, return a user-friendly string that fully describes (if multiple, concatenate with `\n`) the error with an appropriate `4XX, 5XX` code.

- Non-transactional APIs should always return 2XX, as warnings and failures are an expected part of the API.

- APIs that are indicated "Site-dependent" in the notes should look for site header and act accordingly. + **X-DATACENTER is changed to X-SITE that has the SITE_ID**.

# Types

```
ITMODEL {
  id: ITMODEL_ID,

  + type: "regular" | "chassis" | "blade",

  vendor: string,
  model_number: string,
  height: int, // if blade, ignored
  power_ports: int, // if blade, ignored
  network_port_labels: string[] // if blade, ignored

  display_color: string | null,
  cpu: string | null,
  memory: int | null,
  storage: string | null,
  comment: string | null,
}

ASSET {
  id: ASSET_ID,
  asset_number: number,
  hostname: string | null,
  itmodel: ITMODEL_ID,
  + dislay_color: string | null,
  + cpu: string | null,
  + memory: int | null,
  + storage: string | null,
  + location: {
    tag: "rack-mount",
    site: SITE_ID,
    rack: RACK_ID,
    rack_position: int,
  } | {
    tag: "chassis-mount",
    site: SITE_ID,
    asset: ASSET_ID, # must be a chassis,
    slot: int,
  } | {
    tag: "offline",
    site: SITE_ID
  },
  decommissioned: bool,
  power_connections: {
    pdu_id: PDU_ID,
    plug: int,
  }[],
  network_ports: {
    label: string, # symmetry with commit af9c1bcc
    mac_address: string | null,
    connection: NETWORK_PORT_ID | null,
  }[],
  comment: string | null,
  owner: USER_ID | null,
  power_state: "On" | "Off" | null, # null for assets that don't have networked pdus connected to it
}

// For decommissioned assets, these info has to be frozen in time,
// which means it should be resolved based on the change set created when the asset was decommissioned. See 11.5
// Also, obviously, power_state should be null for them.
ASSET_DETAILS {
  id: ASSET_ID,
  asset_number: number,
  hostname: string | null,
  itmodel: ITMODEL,
  + dislay_color: string | null,
  + cpu: string | null,
  + memory: int | null,
  + storage: string | null,
  + location: {
    tag: "rack-mount",
    site: SITE,
    rack: RACK,
    rack_position: int,
  } | {
    tag: "chassis-mount",
    site: SITE,
    asset: ASSET, # must be a chassis,
    slot: int,
  } | {
    tag: "offline",
    site: SITE
  },
  decommissioned: bool,
  decommissioned_by: USER_ID | null, # null if asset not decommissioned
  decommissioned_timestamp: datetime | null, # null if asset not decommissioned
  power_connections: {
    pdu_id: PDU_ID,
    plug: int,
    label: string, # ex) L1, R2
  }[],
  network_ports: {
    id: int,
    label: string,
    mac_address: string | null,
    connection: NETWORK_PORT_ID | null,
    connection_str: string | null, // Some string that represents an asset + network port label
  }[],
  network_graph: NETWORK_GRAPH,
  comment: string | null,
  owner: USER | null,
  power_state: "On" | "Off" | null # null for assets that don't have networked pdus connected to it,
}

RACK {
  id: RACK_ID,
  rack: string,
  site: SITE_ID, # must be of type "datacenter"
  decommissioned: bool
}

SITE {
  id: SITE_ID,
  type: "datacenter" | "offline-storage",
  name: string,
  abbr: string,
}

NETWORK_PORT {
  id: NETWORK_PORT_ID,
  asset_str: ASSET_STR,
  label: string,
  mac_address: string | null,
  connection: NETWORK_PORT_ID | null
}

POWER_PORT {
  pdu_id: PDU_ID,
  plug: int,
  asset_id: ASSET_ID | null,
  label: string, # ex) L1, R2
}

USER {
  username: string,
  first_name: string,
  last_name: string,
  email: string,
  permission: Permission,
}

Permission {
  model_perm: boolean,
  asset_perm: boolean,
  power_perm: boolean,
  audit_perm: boolean,
  admin_perm: boolean
  site_perm: string, # Comma separated list of site abbrs
}

NETWORK_GRAPH {
  verticies: {
    label: ASSET_STR | BLADE_STR, // guaranteed to be unique
    url: .../#/assets/{ASSET_ID} | .../#/blades/{BLADE_ID} (should just work without modification)
  }[],
  edges: [STR, STR][], // str matches labels exactly
}

CHANGE_PLAN {
  id: CHANGE_PLAN_ID,
  name: string,
  executed_at: number | null, # timestamp of the execution
  diffs: {
    live: ASSET_DETAILS | null, # live version
    cp: ASSET_DETAILS | null, # change plan version
    conflicts: {
      field: string,
      message: string
    }[]
  }[]
}


```

# Create APIs

### `[POST] api/equipment/ITModelCreate`

#### Request Body

```
{
  + type: "regular" | "chassis" | "blade",
  vendor: string,
  model_number: string,
  height: int, // ignored if chassis or blade
  power_ports: int, // ignored if blade
  network_port_labels: string[] // ignored if blade

  display_color: string | null,
  cpu: string | null,
  memory: number | null,
  storage: string | null,
  comment: string | null,
}
```

#### Notes

The necessary `NetworkPort` should be generated on the server.

#### Response Body

```
ITModel
```

### `[POST] api/equipment/AssetCreate`

#### Request Body

```
{
  asset_number: number | null,
  hostname: string | null,
  itmodel: ITMODEL_ID,
  + dislay_color: string | null,
  + cpu: string | null,
  + memory: int | null,
  + storage: string | null,
  + location: {
    tag: "rack-mount",
    site: SITE_ID,
    rack: RACK_ID,
    rack_position: int,
  } | {
    tag: "chassis-mount",
    site: SITE_ID,
    asset: ASSET_ID, # must be a chassis,
    slot: int,
  } | {
    tag: "offline",
    site: SITE_ID
  },
  power_connections: {
    pdu_id: PDU_ID,
    plug: int,
  }[],
  network_ports: {
    label: string,
    mac_address: string | null,
    connection: NETWORK_PORT_ID | null
  }[],
  comment: string | null,
  owner: USER_ID | null,
}
```

#### Notes

The necessary `Powereds` / `NetworkPort` should (of course, after validation) should be generated.

Since network port labels are unique within an ITModel, `label` field is sufficient to identify and create the network port.

#### Response Body

```
Asset
```

### `[POST] api/equipment/RackRangeCreate`

#### Request Body

```
{
  site: SITE_ID,
  r1: string,
  r2: string,
  c1: int,
  c2: int
}
```

#### Notes

All racks will be created in the same datacenter.
r1 and r2 refer to row letters, e.g. 'D' or 'AA'.
c1 and c2 refer to column numbers, currently 1 through 99.
The necessary `PDU`s should be created.

#### Response Body

```
{
  created: Rack[],
  warn: string[],
  err: string[]
}
```

### `[POST] api/equipment/SiteCreate`

#### Request Body

```
{
  + type: "datacenter" | "offline-storage"
  abbr: string,
  name: string
}
```

#### Response Body

```
Site
```

# Update APIs

### `[PATCH] api/equipment/ITModelUpdate/:itmodel_id`

#### Request Body

```
{
  + type: "regular" | "chassis" | "blade",

  vendor: string,
  model_number: string,

  height: int,
  power_ports: int,
  network_port_labels: string[],

  display_color: string | null,
  cpu: string | null,
  memory: number | null,
  storage: string | null,
  comment: string | null,
}
```

#### Notes

This request should be rejected if there are instances of this ITModel.

#### Response Body

```
ITModel # updated one
```

### `[PATCH] api/equipment/AssetUpdate/:asset_id`

#### Request Body

```
{
  asset_number: number | null,
  hostname: string | null,
  itmodel: ITMODEL_ID,
  + dislay_color: string | null,
  + cpu: string | null,
  + memory: int | null,
  + storage: string | null,
  + location: {
    tag: "rack-mount",
    site: SITE_ID,
    rack: RACK_ID,
    rack_position: int,
  } | {
    tag: "chassis-mount",
    site: SITE_ID,
    asset: ASSET_ID, # must be a chassis,
    slot: int,
  } | {
    tag: "offline",
    site: SITE_ID
  },
  power_connections: {
    pdu_id: PDU_ID,
    plug: int,
  }[],
  network_ports: {
    label: string,
    mac_address: string | null,
    connection: NETWORK_PORT_ID | null
  }[],
  comment: string | null,
  owner: USER_ID | null,
}
```

#### Response Body

```
Asset # updated one
```

### `[PATCH] api/equipment/SiteUpdate/:site_id`

#### Request Body

```
{
  name: string,
  abbr: string,
}
```

#### Response Body

```
Site # updated one
```

# Destroy APIs

### `[DELETE] api/equipment/ITModelDestroy/:itmodel_id`

#### Notes

The request should fail if there are live assets of this ITModel.

#### Response Body

```
ITMODEL_ID
```

### `[DELETE] api/equipment/AssetDestory/:asset_id`

#### Response Body

```
ASSET_ID
```

### `[POST] api/equipment/RackRangeDestroy`

#### Request Body

```
{
  site: SITE_ID,
  r1: string,
  r2: string,
  c1: int,
  c2: int
}

```

#### Notes

> Not transactional

POST is used to allow for sending data.
r1 and r2 refer to row letters, e.g. 'D' or 'AA'.
c1 and c2 refer to column numbers, currently 1 through 99.

#### Response Body

```
{
  removed: RACK_ID[], # All of the successfully deleted racks
  warn: string[], # Racks that are decommissioned
  err: string[] # Racks that are skipped
}
```

####

### `[DELETE] api/equipment/SiteDestory/:site_id`

#### Response Body

```
SITE_ID
```

# Retrieve APIs

### `[GET] api/equipment/ITModelRetrieve/:itmodel_id`

#### Response Body

```
ITModel
```

### `[GET] api/equipment/AssetRetrieve/:asset_id`

#### Response Body

```
ASSET
```

### `[GET] api/equipment/AssetDetailRetrieve/:asset_id`

#### Response Body

```
ASSET_DETAILS
```

# List APIs

For all of these APIs, make sure they don't fail - just act as if empty list is returned with 200.

Also, filters with undefined query params shouldn't filter out anything.

### `[GET] api/equipment/ITModelList`

#### Query params

```
{
  search: string | undefined,
  page: int | undefined, # default 1,
  page_size: int | undefined, # default 10
  height_min: number | undefined,
  height_max: number | undefined,
  memory_min: number | undefined,
  memory_max: number | undefined,
  network_ports_min: number | undefined,
  network_ports_max: number | undefined,
  power_ports_min: number | undefined,
  power_ports_max: number | undefined,
  ordering:
    | '[-]vendor'
    | '[-]model_number'
    | '[-]height'
    | '[-]display_color'
    | '[-]network_ports'
    | '[-]power_ports'
    | '[-]cpu'
    | '[-]memory'
    | '[-]storage'
    | undefined, # default 'id'
}
```

#### Response body

```
{
  count: int,
  next: hyperlink | null,
  previous: hyperlink | null,
  results: ITModelEntry[],
}

where

ITModelEntry {
  id: ITMODEL_ID,
  vendor: string,
  model_number: string,
  height: int,
  display_color: string | null,
  network_ports: int,
  power_ports: int,
  cpu: string | null,
  memory: int | null,
  storage: string | null,
}
```

#### Notes

Ordering can take multiple values, separated by commas. The returned list will be sorted primarily by the first value, and ties will be broken by each consecutive value.

Each value uses ascending order by default. To use descending order, an optional "-" mark should be included in front of the value. For example: -height,-cpu

### `[GET] api/equipment/AssetList`

#### Query params

```
{
  search: string | undefined,
  page: int | undefined, # default 1,
  page_size: int | undefined, # default 10
  itmodel: ITMODEL_ID | undefined,
  r1: string | undefined,
  r2: string | undefined,
  c1: int | undefined,
  c2: int | undefined,
  - rack_position_min: int | undefined # Not used
  - rack_position_max: int | undefined # Not used
  ordering:
    | '[-]itmodel__vendor',
    | '[-]itmodel__model_number',
    | '[-]hostname',
    | '[-]site__abbr',
    | '[-]rack__rack', # Note: The order is lexographic so you will get A, AA, B and this bug is not worth fixing
    | '[-]rack_position',
    | '[-]owner',
    | undefined # default 'id'
}
```

#### Notes

> Site-dependent

r1, r2, c1, and c2 must all be defined if any of them is defined. They filter based on a rack range.

Exclude Decommissioned Assets

Ordering can take multiple values, separated by commas. The returned list will be sorted primarily by the first value, and ties will be broken by each consecutive value.

Each value uses ascending order by default. To use descending order, an optional "-" mark should be included in front of the value. For example: -height,-cpu

`power_action_visible` field in the response can be determined since the request contains the user session.

#### Response body

```
{
  count: int,
  next: hyperlink | null,
  previous: hyperlink | null,
  result: AssetEntry[],
}

where

AssetEntry {
  id: ASSET_ID,
  model: string,
  hostname: string,
  location: string,
  owner: string,
  power_action_visible: bool
}
```

### `[GET] api/equipment/DecommissionedAssetList`

#### Query params

```
{
  page: number,
  page_size: number,
  username: string | undefined, # Currently assuming this is owner, not decommissioned_by
  timestamp_from: number | undefined, # Time zone dependent (Django default - see SystemLog for format)
  timestamp_to: number | undefined,
  ordering:
      | '[-]itmodel__vendor',
      | '[-]itmodel__model_number',
      | '[-]hostname',
      | '[-]site__abbr',
      | '[-]rack__rack', # Note: The order is lexographic so you will get A, AA, B and this bug is not worth fixing
      | '[-]rack_position',
      | '[-]owner',
      | '[-]decommissioned_by,
      | '[-]decommissioned_timestamp,
      | undefined # default 'id'
}
```

#### Response body

```
{
  count: int,
  next: hyperlink | null,
  previous: hyperlink | null,
  result: DecommissionedAssetEntry[],
}

where

DecommissionedAssetEntry = AssetEntry + {
  decom_by: string,
  decom_timestamp: number,
}
```

#### Notes

Ordering can take multiple values, separated by commas. The returned list will be sorted primarily by the first value, and ties will be broken by each consecutive value.

Each value uses ascending order by default. To use descending order, an optional "-" mark should be included in front of the value. For example: -height,-cpu

### `[GET] api/equipment/AssetPickList`

#### QueryParams

```
{
  site_id: SITE_ID | undefined,
  rack_id: RACK_ID | undefined,
}
```

#### Notes

Obviously, they're both filters.

#### Response body

```
Asset[]
```

### `[GET] api/equipment/RackList`

#### Notes

> Site-dependent

#### Response body

```
Rack[]
```

### `[GET] api/equipment/SiteList`

#### Response body

```
Site[]
```

### `[GET] api/power/PowerPortList`

#### Query params

```
{
  rack_id: RACK_ID | undefined
}
```

#### Response body

```
PowerPort[]
```

### `[GET] api/network/NetworkPortList`

#### Notes

> Site-dependent

```
{
  asset_id: ASSET_ID | undefined
}
```

#### Response body

```
NetworkPort[]
```

### `[GET] api/equipment/ITModelPickList`

```
{
  id: MODEL_ID,
  str: MODEL_STR,
}
```

# Log APIs

### `[GET] api/log/EntryList`

#### Query params

```
{
  page: int,
  page_size: int,
  username_search: string | undefined,
  display_name_search: string | undefined,
  model_search: string | undefined,
  identifier_search: string | undefined,
  ordering:
    | 'timestamp'
    | undefined # default 'timestamp'
  direction:
    | 'ascending'
    | 'descending'
    | undefined # default 'descending'
}
```

# Power Management APIs

### `[GET] api/network/PDUNetwork/get/:asset_id`

#### Notes

It's guaranteed that this api will be called only on assets that had `power_state` field set to a non-null field.

#### Response body

```
"On" | "Off" | "Unavailable"
```

### `[POST] api/network/PDUNetwork/post`

#### Request body

```
{
  asset_id: ASSET_ID,
  state: "on" | "off"
}
```

#### Response body

```
(empty)
```

### `[POST] api/network/PDUNetwork/cycle`

#### Request body

```
{
  asset_id: ASSET_ID
}
```

#### Notes

The response shouldn't be sent until the cycle operation is finished.

#### Response body

```
(empty)
```

# User APIs

### `[GET] auth/current_user`

#### Notes

#### Response body

```
User | null
```

### `[POST] auth/login`

#### Request body

```
{
  username: string,
  password: string,
}
```

#### Response body

```
User
```

### `[POST] auth/logout`

#### Response body

```
(empty)
```

### `[GET] auth/shib_login`

#### Notes

Should redirect to /Shibboleth.sso/Login

# Import / Export APIs

### `[POST] api/import/ITModel`

### `[POST] api/import/Asset`

### `[POST] api/import/Network`

#### Query params

```
{
  force: boolean # when true, ignore warnings
}
```

#### Request body

```
serialized bytestream of the csv file
```

#### Notes

This request should always "succeed" with status code 2XX.

#### Response body

```
{
  headers: string[],
  diff: {
    before: string[] | null,
    after: string[] | null,
    warning: string | null,
    error: string | null,
  }[]
}
```

### `[GET] api/export/ITModel.csv`

### `[GET] api/export/Asset.csv`

### `[GET] api/export/Network.csv`

#### Query params

```
See respective Filter APIs (but without page/page_size/ordering/direction)
Network inherits the filters from Assets - for the exact semantics, see https://piazza.com/class/k4u27qnccr45oo?cid=110
```

#### Response body

```
serialized bytestream of the csv file (make sure that the content-type header is set to 'application/octet-stream' to trigger the download.)
```

# Decommissioning

### `[POST] api/equipment/DecommissionAsset/:asset_id`

#### Response body

```
ASSET_DETAILS
```

# Change plan APIs

## General note:

Every request that a user makes while in a change plan will include a header `X-CHANGE-PLAN` (`HTTP_X_CHANGE_PLAN` in django), with id of the change plan on it.
If not present, it means that the user is working on live data.

Any updates to live data other than assets should be rejected when the header is present. (Creating/Updating/Deleting ITModels/Racks/Sites, network power management), although such action should be prevented from the UI as well.

All asset-related APIs (
AssetRetrieve,
AssetDetailRetrieve,
AssetList,
AssetCreate,
AssetUpdate,
AssetDestroy,
AssetPickList, PowerPortList, NetworkPortList,
DecommissionedAssetList,
DecommissionAsset,
Logs
) should behave differently when the header is present.

### `[GET] api/changeplan/ChangePlanList`

#### Notes

Only return the change plans made by the requesting user.

#### Response body

```
ChangePlanEntry[]

where

ChangePlanEntry {
  id: CHANGE_PLAN_ID,
  name: string,
  executed_at: number | null, # timestamp of the execution
  has_conflicts: bool
}
```

### `[GET] api/changeplan/ChangePlanDetails/:change_plan_id`

#### Response body

```
CHANGE_PLAN
```

### `[GET] api/changeplan/ChangePlanActions/:change_plan_id`

#### Response body

```
string[] // See 10.7
```

### `[POST] api/changeplan/ChangePlanCreate`

#### Request body

```
{
  name: string
}
```

#### Response body

```
CHANGE_PLAN_ID
```

### `[POST] api/changeplan/ChangePlanExecute/:change_plan_id`

#### Notes

Reject if there are conflicts

#### Response body

```
CHANGE_PLAN
```

### `[PATCH] api/changeplan/ChangePlanUpdate/:change_plan_id`

#### Request body

```
{
  name: string
}
```

#### Response body

```
(Empty)
```

### `[DELETE] api/changeplan/ChangePlanDestroy/:change_plan_id`

#### Response body

```
(Empty)
```

# Rack usage report API

### `[GET] api/equipment/report`

> Site-Dependent
> ... change plan dependent? (I don't think this is necessary tho)
> It would be best if the list could be sorted in descending order of used

#### Response body

```
{
    total: DataRow[],
    by_model: DataRow[],
    by_owner: DataRow[],
    by_vendor: DataRow[],
}

where

DataRow {
    category: string, # (for total, it'd be just "total" and for model, a string representing a single model, and so on)
    used: number, # a number in [0, 1]
    free: number, # a number in [0, 1]
}
```

# Rack view API

### `[POST] api/equipment/rack_view`

#### Request body

```
{
    rack_ids: RACK_ID[]
}
```

#### Response body

```
{
    rack_id1: RackDesc,
    rack_id2: RackDesc,
    rack_id3: RackDesc,
    ...
}

where

RackDesc {
    rack: RACK,
    assets: AssetDesc[],
}

where

AssetDesc {
    asset: ASSET,
    model: MODEL,
}
```

# User API

### `[POST] auth/UserCreate`

#### Request Body

```
{
  user: User,
  password: string,
}
```

#### Response Body

```
User
```

### `[GET] auth/UserRetrieve/:user_id`

#### Response Body

```
User
```

### `[GET] auth/api/UserList`

#### Response body

```
User[]
```

### `[POST] auth/UserUpdate`

#### Request Body

```
User
```

#### Response Body

```
User
```

### `[DELETE] auth/UserDestroy/:user_id`
