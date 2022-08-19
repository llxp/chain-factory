import React from "react";
import { AppBar, Divider } from "@material-ui/core";
import AccountBoxIcon from "@material-ui/icons/AccountBox";
import { LargeMenuItem } from "./LargeMenuItem";
import { CustomMenuButton } from "./CustomMenuButton";
import { CustomToolbar } from "./CustomToolbar";
import NamespaceSelector from "../NamespaceSelector";
import LogoutMenu from "./LogoutMenu";
import { useState } from "react";
import { useLocation } from "react-router-dom";

export default function LargeToolbar(props) {
  const [signOutButtonRef, setSignOutButtonRef] = useState<null | HTMLElement>(null);
  const location = useLocation();
  const handleShowLogoutMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setSignOutButtonRef(event.currentTarget);
  };

  if (location.pathname === "/signin") {
    return <></>;
  }

  return (
    <AppBar>
      <CustomToolbar>
        <Divider orientation="vertical" variant="fullWidth" flexItem key="ctd1"/>
        <span style={{ flexGrow: 0.05 }} key="cts0"/>
        <NamespaceSelector key="namespaceSelector"/>
        <span style={{ flexGrow: 0.6 }} key="cts1"/>
        <LargeMenuItem text="Dashboard" path="/orchestrator/dashboard" key="/orchestrator/dashboard"/>
        <LargeMenuItem text="Workflows" path="/orchestrator/workflows" key="/orchestrator/workflows"/>
        <LargeMenuItem text="New" path="/orchestrator/new" key="/orchestrator/new"/>
        <span style={{ flexGrow: 1 }} key="cts2"/>
        <Divider orientation="vertical" variant="fullWidth" flexItem key="ctd2"/>
        <CustomMenuButton variant="text" key="ctcmb" onClick={handleShowLogoutMenu} to="">
          <AccountBoxIcon/>
        </CustomMenuButton>
        <LogoutMenu anchorEl={signOutButtonRef} key="ctlm" setAnchorEl={setSignOutButtonRef}/>
      </CustomToolbar>
    </AppBar>
  );
}