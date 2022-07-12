import { ListItem, Fab, Box, ListItemText } from "@material-ui/core";
import React from "react";

export interface NodeListItemProps {
  node: any;
  status: string;
}

export default function NodeListItem(props: NodeListItemProps) {
  return (
    <ListItem>
      <Fab variant="circular" disabled size="small" style={{ backgroundColor: props.status === 'Running' ? '#00aa00' : '#aa0000', fontWeight: 'bold', marginRight: 15 }}>
        <Box fontWeight="bold"></Box>
      </Fab>
      <ListItemText primary={props.node} secondary={props.status} />
    </ListItem>
  );
}