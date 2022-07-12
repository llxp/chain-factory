import { Grid } from "@material-ui/core";
import React from "react";

export interface IErrorProps {
  error: string;
}

export default function Error(props: IErrorProps) {
  const { error } = props;
  return (
    <Grid container justifyContent="center" style={{ minHeight: '50vh' }} spacing={0} direction="column" alignItems="center">
      <Grid item md><p>{error.toString()}</p></Grid>
    </Grid>
  );
}