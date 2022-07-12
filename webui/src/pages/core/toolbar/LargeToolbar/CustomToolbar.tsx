import { Toolbar } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";

export const CustomToolbar = (props) => {
  const useStyles = makeStyles({
    root: {
      'padding-left': '0px',
      'padding-right': '0px',
      'margin-right': '0px'
    },
    label: {
      textTransform: 'capitalize',
    },
  });

  const classes = useStyles();

  return (<Toolbar classes={{root: classes.root}}>{props.children}</Toolbar>);
};