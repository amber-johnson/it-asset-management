import React, { useContext } from "react";
import {AuthContext, SiteContext} from "../../contexts/contexts";
import {getAsset} from "../../api/asset";
import {getSites} from "../../api/site";

export async function CheckOwnerPermissions(asset) {

    const {user} = useContext(AuthContext);
    const username = user?.username;
    //const asset = await getAsset(assetID);
    const owner = asset?.owner;

    let isPermitted = false;
    if (username === owner) {
        isPermitted = true;
    }
    return isPermitted;
}

// a function to check if a user can CUD sites (datacenters and offline storage)
export async function CheckSitePermissions(site) {

    const { user } = useContext(AuthContext);
    const permittedSitesAsString = user?.permission?.site_perm;
    const permittedSitesAsArray = permittedSitesAsString.split(",");
   // console.log("permitted sites", permittedSitesAsArray);
    const isPermittedGivenAbbr = permittedSitesAsArray.includes(site);
   // console.log("sitePermittedGivenAbbr", sitePermittedGivenAbbr);

    const siteList = await getSites();
   // console.log("site list", siteList);
    let permittedSiteIDsAsArray = [];
    for (let i = 0; i < permittedSitesAsArray.length; i++) {
        for (let j = 0; j < siteList.length; j++) {
            if (permittedSitesAsArray[i] == siteList[j].abbr)
            permittedSiteIDsAsArray.push(siteList[j].id);
        }
    }
   // console.log("permittedSiteIDsAsArray", permittedSiteIDsAsArray);

    const isPermittedGivenID = permittedSiteIDsAsArray.includes(site);
   // console.log("sitePermittedGivenID", sitePermittedGivenID);
    return isPermittedGivenAbbr || isPermittedGivenID || (!!user?.permission?.admin_perm);

}


function ConfigureUserPermissions() {

    const { user } = useContext(AuthContext); //returns user object from auth/current_user
    console.log(user);


    // api calls to check permissions
    const hasModelPerm = !!user?.permission?.model_perm; //if true -> true, if null/false -> false
    const hasAssetPerm = !!user?.permission?.asset_perm;
    const hasPowerPerm = !!user?.permission?.power_perm;
    const hasAuditPerm = !!user?.permission?.audit_perm;
    const hasAdminPerm = !!user?.permission?.admin_perm;

    //TODO: add owner permissions

    // api calls to check asset owner
    //const owner =
    const isAssetOwner = true;

    //configure signals for viewable tabs
    const canLogView = !!(hasAuditPerm || hasAdminPerm);
    const canChangePlan = !!(hasAssetPerm || hasAdminPerm);

    //configure signals for editable views
    const canModelCUD = !!(hasModelPerm || hasAdminPerm);
    const canAssetCUDD = !!(hasAssetPerm || hasAdminPerm);
    const canOfflineCUDD = !!(hasAssetPerm || hasAdminPerm);
    const canSiteCUD = CheckSitePermissions("Global"); //must have global access to create a site
    const canRackCUD = !!(hasAssetPerm || hasAdminPerm);

    //configure signals for within detail views
    const canAssetPower = !!(hasPowerPerm || hasAdminPerm);

    const config = {
        canLogView,
        canChangePlan,
        canModelCUD,
        canAssetCUDD,
        canOfflineCUDD,
        canSiteCUD,
        canRackCUD,
        canAssetPower,
    }

    console.log(config);
    return config;
}

export default ConfigureUserPermissions;