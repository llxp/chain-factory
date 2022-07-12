import React from 'react';
import { IconButton } from '@material-ui/core';
import RefreshIcon from '@material-ui/icons/Refresh';

export interface IRefreshButtonProps {
  onRefresh?: () => void;
}
export default function RefreshButton(props: IRefreshButtonProps) {
  return <IconButton size="small" onClick={props.onRefresh} style={{backgroundColor: '#e91e63', /*width: 56, height: 56, marginLeft: -10,*/ marginTop: 5, marginLeft: 10, marginRight: 10, marginBottom: 10}}><RefreshIcon/></IconButton>;
}