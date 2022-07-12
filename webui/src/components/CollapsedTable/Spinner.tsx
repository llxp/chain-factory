import { CircularProgress, Grid } from "@material-ui/core";
import React from "react";

export default function Spinner() {
  return (
    <Grid container justifyContent="center" style={{ minHeight: '50vh' }} spacing={0} direction="column" alignItems="center">
      <Grid item md={1}><CircularProgress/></Grid>
    </Grid>
  );
}