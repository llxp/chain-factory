import React from "react";
import withRouter from "./withrouter";
import './style/ResponsiveAppBar.css';
import Drawer from "./Drawer";
import LargeToolbar from "./LargeToolbar";
import { Hidden } from "@material-ui/core";

function ResAppBar(props) {

  return (<>
    <Hidden only={["xl", "lg", "md"]}>
      <Drawer/>
    </Hidden>
    <Hidden only={["sm", "xs"]}>
      <LargeToolbar/>
    </Hidden>
  </>);
}

export const ResponsiveAppBar = withRouter(ResAppBar);

export default ResponsiveAppBar;