import { createStyles, makeStyles, Theme } from "@material-ui/core";
import React from "react";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      paddingLeft: theme.spacing(2),
      paddingRight: theme.spacing(1),
      backgroundColor: theme.palette.primary.main,
      borderTop: '1px solid #ddd',
      position: 'fixed',
      height: 60,
      bottom: 0,
      width: '100%',
      clear: 'both'
    },
  }),
);

export default function Footer() {
  const classes = useStyles();
  return (
    <footer className={classes.root}>
      Footer content
    </footer>
  );
}
