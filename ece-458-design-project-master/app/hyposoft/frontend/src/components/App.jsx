import React from "react";
import { HashRouter as Router, Switch, Route } from "react-router-dom";

import LoginPage from "./auth/LoginPage/LoginPage";
import ManagementPageFrame from "./management/ManagementPageFrame";
import ModelManagementPage from "./management/ModelManagement/ModelManagementPage";
import ModelDetailPage from "./management/ModelManagement/ModelDetailPage";
import AssetManagementPage from "./management/AssetManagement/AssetManagementPage";
import ReportManagementPage from "./management/ReportManagement/ReportManagementPage";
import LandingPage from "./management/LandingPage/LandingPage";
import BarcodeView from "./management/AssetManagement/BarcodeView";
import AssetDetailPage from "./management/AssetManagement/AssetDetailPage";
import CreateModelPage from "./management/ModelManagement/CreateModelPage";
import CreateAssetPage from "./management/AssetManagement/CreateAssetPage";
import RackManagementPage from "./management/RackManagement/RackManagementPage";
import RackView from "./management/RackManagement/RackView";
import LogManagementPage from "./management/LogManagement/LogManagementPage";
import DecommissionManagementPage from "./management/DecommissionManagement/DecommissionManagementPage";
import SiteManagementPage from "./management/SiteManagment/SiteManagementPage";
import {
  AuthContext,
  SiteContext,
  ChangePlanContext,
} from "../contexts/contexts";

export const SITE_SESSION_KEY = "SITE";

export const CHANGE_PLAN_SESSION_KEY = "CHANGE_PLAN";
export const CHANGE_PLAN_NAME_SESSION_KEY = "CHANGE_PLAN_NAME";

import { getCurrentUser } from "../api/auth";
import { getSites } from "../api/site";
import Testing from "./utility/Testing";
import WorkOrderPage from "./management/ChangePlan/WorkOrderPage";
import ChangePlanList from "./management/ChangePlan/ChangePlanList";
import CreateChangePlan from "./management/ChangePlan/CreateChangePlan";
import ChangePlanDetail from "./management/ChangePlan/ChangePlanDetail";
import useTrigger from "./utility/useTrigger";
import ModelImportPage from "./management/Import/ModelImportPage";
import AssetImportPage from "./management/Import/AssetImportPage";
import NetworkImportPage from "./management/Import/NetworkImportPage";
import AssetDetailView from "./management/DecommissionManagement/DecommissionList/AssetDetailView";
import OfflineAssetManagementPage from "./management/OfflineAssetManagement/OfflineAssetManagementPage";
import Scanner from "./mobile/Scanner";
import UserManagementPage from "./management/UserManagement/UserManagementPage";
import CreateUserPage from "./management/UserManagement/CreateUserPage";
import UserDetailPage from "./management/UserManagement/UserDetailPage";

function App() {
  const [loading, setLoading] = React.useState(true);
  const [currentUser, setCurrentUser] = React.useState(null);
  const [site, setSite] = React.useState(null);
  const [siteTrigger, fireSiteTrigger] = useTrigger();
  const [changePlan, setChangePlan] = React.useState(null);
  const [cpTrigger, fireCPTrigger] = useTrigger();

  React.useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        await getCurrentUser().then(setCurrentUser);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  React.useEffect(() => {
    (async () => {
      const siteID = parseInt(sessionStorage.getItem(SITE_SESSION_KEY));
      if (!isNaN(siteID)) {
        const site = await getSites().then(
          sites => sites.find(site => site.id == siteID) ?? null,
        );
        setSite(site);
      }
    })();
  }, []);

  React.useEffect(() => {
    const id = sessionStorage.getItem(CHANGE_PLAN_SESSION_KEY);
    const name = sessionStorage.getItem(CHANGE_PLAN_NAME_SESSION_KEY);
    const cp = id && name ? { id, name } : null;
    setChangePlan(cp);
  }, []);

  if (loading) {
    return <div />;
  }

  const authContextValue = {
    user: currentUser,
    setUser: setCurrentUser,
  };

  const siteContextValue = {
    site,
    setSiteByID: async siteID => {
      if (siteID) {
        const site = await getSites().then(
          sites => sites.find(site => site.id == siteID) ?? null,
        );
        if (site) {
          sessionStorage.setItem(SITE_SESSION_KEY, site.id);
          setSite(site);
          return;
        }
      }

      sessionStorage.removeItem(SITE_SESSION_KEY);
      setSite(null);
    },
    refreshTrigger: siteTrigger,
    refresh: fireSiteTrigger,
  };

  const cpContextValue = {
    changePlan,
    setChangePlan: cp => {
      console.log(cp);
      if (cp) {
        const { id, name } = cp;
        sessionStorage.setItem(CHANGE_PLAN_SESSION_KEY, id);
        sessionStorage.setItem(CHANGE_PLAN_NAME_SESSION_KEY, name);
        setChangePlan(cp);
      } else {
        sessionStorage.removeItem(CHANGE_PLAN_SESSION_KEY);
        sessionStorage.removeItem(CHANGE_PLAN_NAME_SESSION_KEY);
        setChangePlan(null);
      }
    },
    refreshTrigger: cpTrigger,
    refresh: fireCPTrigger,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      <SiteContext.Provider value={siteContextValue}>
        <ChangePlanContext.Provider value={cpContextValue}>
          {currentUser ? (
            <Router>
              <Switch>
                <Route exact path="/testing">
                  <Testing />
                </Route>
                <Route exact path="/racks/print_view">
                  <RackView />
                </Route>
                <Route exact path="/changeplan/workorder">
                  <WorkOrderPage />
                </Route>
                <Route exact path="/assets/print_view">
                  <BarcodeView />
                </Route>
                <Route exact path="/scanner">
                  <Scanner />
                </Route>
                <Route exact path="/scanner/assets/:id">
                  <AssetDetailView />
                </Route>
                <Route>
                  <ManagementPageFrame>
                    <Switch>
                      <Route exact path="/models">
                        <ModelManagementPage />
                      </Route>
                      <Route exact path="/models/create">
                        <CreateModelPage />
                      </Route>
                      <Route exact path="/models/:id">
                        <ModelDetailPage />
                      </Route>
                      <Route exact path="/assets">
                        <AssetManagementPage />
                      </Route>
                      <Route exact path="/assets/create">
                        <CreateAssetPage />
                      </Route>
                      <Route exact path="/assets/:id">
                        <AssetDetailPage origin="/assets" />
                      </Route>
                      <Route exact path="/assets/readonly/:id">
                        <AssetDetailView />
                      </Route>
                      <Route exact path="/offline_assets">
                        <OfflineAssetManagementPage />
                      </Route>
                      <Route exact path="/offline_assets/:id">
                        <AssetDetailPage origin="/offline_assets" />
                      </Route>
                      <Route exact path="/sites">
                        <SiteManagementPage />
                      </Route>
                      <Route exact path="/racks">
                        <RackManagementPage />
                      </Route>
                      <Route exact path="/reports">
                        <ReportManagementPage />
                      </Route>
                      <Route exact path="/logs">
                        <LogManagementPage />
                      </Route>
                      <Route exact path="/decommission">
                        <DecommissionManagementPage />
                      </Route>
                      <Route exact path="/changeplan">
                        <ChangePlanList />
                      </Route>
                      <Route exact path="/changeplan/create">
                        <CreateChangePlan />
                      </Route>
                      <Route exact path="/changeplan/:id">
                        <ChangePlanDetail />
                      </Route>
                      <Route exact path="/import/model">
                        <ModelImportPage />
                      </Route>
                      <Route exact path="/import/asset">
                        <AssetImportPage />
                      </Route>
                      <Route exact path="/import/network">
                        <NetworkImportPage />
                      </Route>
                      <Route exact path="/users">
                        <UserManagementPage />
                      </Route>
                      <Route exact path="/users/create">
                        <CreateUserPage />
                      </Route>
                      <Route exact path="/users/:id">
                        <UserDetailPage />
                      </Route>
                      <Route>
                        <LandingPage />
                      </Route>
                    </Switch>
                  </ManagementPageFrame>
                </Route>
              </Switch>
            </Router>
          ) : (
            <LoginPage />
          )}
        </ChangePlanContext.Provider>
      </SiteContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;
