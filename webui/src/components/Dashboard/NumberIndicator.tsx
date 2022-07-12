import { Box, Fab, Grid, Typography } from "@material-ui/core";
import React from "react";

export interface NumberIndicatorProps {
  value: number;
  label: string;
  backgroundColor: string;
}

export default function NumberIndicator(props: NumberIndicatorProps) {
  return (<Grid container direction="column" spacing={0} alignItems="center">
    <Grid item>
      <Fab variant="circular" disabled style={{ backgroundColor: props.backgroundColor, fontWeight: 'bold', fontSize: 30 }}>
        <Box fontWeight="bold">{props.value}</Box>
      </Fab>
    </Grid>
    <Grid item>
      <Typography>{props.label}</Typography>
    </Grid>
  </Grid>);
}