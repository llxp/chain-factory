import { Box, Theme, Toolbar, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import RefreshButton from "./RefreshButton";
import SearchBox from "./SearchBox";

const useStyles = makeStyles((theme: Theme) => ({
  title: {
    flex: '1 1 100%',
  },
  toolbar: {
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
    backgroundColor: theme.palette.background.paper,
    borderRadius: "4px 4px 0 0",
    //transition: "box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms",
    //boxShadow: "0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)",
  },
}));

export default function TableToolbar({onRefresh, onSearch, title, selectedRows, selectedRowsComponent, searchValue}) {
  const classes = useStyles();

  const SelectedRowsAction = () => {
    if (selectedRows?.length > 0) {
      return selectedRowsComponent;
    }
    return <></>;
  };

  return (
    <Toolbar className={classes.toolbar}>
      <Box display="flex" p={0} style={{width: '100%', height: 'auto'}}>
        <Box p={0}><RefreshButton onRefresh={onRefresh} key="rb"/>
        <SearchBox onSearch={onSearch} value={searchValue} key="sb"/></Box>
        <Box p={0} flexGrow={1}><Typography variant="h4" color="inherit" component="div" className={classes.title} key="title">{title}</Typography></Box>
        <Box p={0} alignContent="flex-end"><SelectedRowsAction key="sra"/></Box>
      </Box>
    </Toolbar>
  );
}