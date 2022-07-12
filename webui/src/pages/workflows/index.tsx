import { Grid, Hidden } from "@material-ui/core";
import React, { useEffect } from "react";
import WorkflowTable from "./WorkflowTable";

export function Workflows() {
  useEffect(() => {
    document.title = "Workflows"
  }, []);
  
  return (
    <div>
      <Hidden xsDown>
      <Grid container direction="row" spacing={0} justifyContent="center" alignItems="center" wrap="nowrap" style={{marginTop: 50}}>
        <Grid item md={1}/>
        <Grid item md={10}>
          <WorkflowTable/>
        </Grid>
        <Grid item md={1}/>
      </Grid>
      </Hidden>
      <Hidden smUp><WorkflowTable/></Hidden>
    </div>
  );
}

export default Workflows;