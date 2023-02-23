import { Box, Button, Divider } from "@material-ui/core";
import React from "react";

export interface TableHeadButtonControlProps {
  onStop: () => void;
  onAbort: () => void;
  onRestart: () => void;
  onDelete: () => void;
}

export default function TableHeadButtonControl(props: TableHeadButtonControlProps) {
  const { onStop, onAbort, onRestart, onDelete } = props;
  return (
      <Box p={0} style={{width: '100%'}} display="flex" justifyContent="flex-start">
        <Box p={0} style={{marginRight: 10}}><Divider orientation="vertical" variant="fullWidth"/></Box>
        <Box p={0} style={{marginRight: 10}}><Button onClick={onDelete} variant="contained" color="primary">Delete</Button></Box>
        <Box p={0} style={{marginRight: 10}}><Button onClick={onStop} variant="contained" color="primary">Stop</Button></Box>
        <Box p={0} style={{marginRight: 10}}><Button onClick={onAbort} variant="contained" color="primary">Abort</Button></Box>
        <Box p={0}><Button onClick={onRestart} variant="contained" color="primary">Restart</Button></Box>
      </Box>
  );
}