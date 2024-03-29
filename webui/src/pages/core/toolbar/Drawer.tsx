import { AppBar, Grid, List, ListItem, SwipeableDrawer, Toolbar, Typography } from "@material-ui/core";
import MenuIcon from "@material-ui/icons/Menu";
import React, { useState } from "react";
import { Link } from "react-router-dom";

import { useDispatch } from "react-redux";
import { signOutAsync } from "../../signin/signin.slice";
import { SmallMenuItem } from "./Drawer/SmallMenuItem";
import NamespaceSelector from "./NamespaceSelector";

export default function Drawer(props) {

  const [drawer, setDrawer] = useState(false);
  const dispatch = useDispatch();
  const handleSignOut = () => {
    dispatch(signOutAsync());
  };

  return (
    <div>
      <AppBar>
        <Toolbar>
          <Grid container direction="row" justifyContent="space-between" alignItems="center" alignContent="center" style={{
            height: "100px"
          }}>
            <Grid item xs={1}><MenuIcon onClick={() => { setDrawer(true); }}/></Grid>
            <Grid item xs={11}><Grid container><NamespaceSelector key="namespaceSelector"/></Grid></Grid>
          </Grid>
        </Toolbar>
      </AppBar>

      <SwipeableDrawer open={drawer} onClose={() => { setDrawer(false); }} onOpen={() => { setDrawer(true); }}>
        <div tabIndex={0} role="button" onClick={() => { setDrawer(false); }} onKeyDown={() => { setDrawer(false); }}>
          <List>
            <SmallMenuItem text="Dashboard" path="/orchestrator/dashboard"/>
            <SmallMenuItem text="Workflows" path="/orchestrator/workflows"/>
            <SmallMenuItem text="New" path="/orchestrator/new"/>
            <ListItem key="Signout" component={Link} to="/signin" divider button onClick={handleSignOut}>Signout</ListItem>
          </List>
        </div>
      </SwipeableDrawer>
    </div>
  );
}