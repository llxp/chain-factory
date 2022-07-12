import { makeStyles, Theme } from "@material-ui/core";
import { createStyles } from "@material-ui/styles";
import React from "react";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
      backgroundColor: theme.palette.background.paper,
    },
    roundShapeRunning: {
      backgroundColor: '#ffff00',
      width: 40,
      height: 40,
      display: 'inline-block',
      borderRadius: '50%',
      animation: `$myEffect 1.5s linear infinite`,
    },
    roundShapeSuccess: {
      backgroundColor: '#00aa00',
      width: 40,
      height: 40,
      display: 'inline-block',
      borderRadius: '50%',
      float: 'left',
    },
    roundShapeFailure: {
      backgroundColor: '#aa0000',
      width: 40,
      height: 40,
      display: 'inline-block',
      borderRadius: '50%',
      float: 'left',
    },
    "@keyframes myEffect": {
      "50%": {
        opacity: 0.3
      },
    }
  }),
);

export default function StatusIndicator({ status }) {
  const classes = useStyles();
  switch(status?.toLowerCase()) {
    case 'task':
    case 'none':
      return <div className={classes.roundShapeSuccess}/>;
    case 'exception':
    case 'timeout':
    case 'false':
    case 'aborted':
    case 'stopped':
      return <div className={classes.roundShapeFailure}/>;
    case 'running':
      return <div className={classes.roundShapeRunning}/>;
  }
  return <></>;
};