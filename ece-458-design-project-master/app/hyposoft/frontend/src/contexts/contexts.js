import React from "react";

export const AuthContext = React.createContext({
  user: null,
  setUser: () => {},
});

export const SiteContext = React.createContext({
  site: null,
  setSiteByID: () => {},
  refreshTrigger: 0,
  refresh: () => {},
});

export const ChangePlanContext = React.createContext({
  changePlan: null, // just id and name
  setChangePlan: () => {},
  refreshTrigger: 0,
  refresh: () => {},
});

export const DisableContext = React.createContext({
  disabled: false,
});

export const NetworkedPDUContext = React.createContext({
  ids: [],
});
