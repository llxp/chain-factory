import { Grid, List, Theme } from "@material-ui/core";
import React, { useEffect, useRef } from "react";
import { PagedTaskLogs } from "./models";
import { scrollToBottom } from "./utils";
import uuid from 'react-uuid';
import { makeStyles } from "@material-ui/styles";

export interface ITaskLogProps {
  taskLogs: PagedTaskLogs;
};

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    background: "linear-gradient(to right, #999999 4px, transparent 0px) 0 0," +
    "linear-gradient(to right, #999999 4px, transparent 0px) 0 100%," +
    "linear-gradient(to left, #999999 1px, transparent 1px) 100% 0," +
    "linear-gradient(to left, #999999 1px, transparent 1px) 100% 100%, " +
    "linear-gradient(to bottom, #999999 1px, transparent 1px) 0 0, " +
    "linear-gradient(to bottom, #999999 1px, transparent 1px) 100% 0, " +
    "linear-gradient(to top, #999999 4px, transparent 1px) 0 100%, " +
    "linear-gradient(to top, #999999 4px, transparent 0px) 100% 100%",
    backgroundRepeat: "no-repeat",
    backgroundSize: "50% 50%",
    marginLeft: 72
  }
}));

export default function TaskLog(props) {
  const scrollRef = useRef<HTMLUListElement>(null);
  useEffect(() => {
    if (scrollRef && scrollRef.current && scrollRef.current !== null) {
      scrollToBottom(scrollRef.current);
    }
  }, [props.taskLogs]);

  const classes = useStyles();
  
  return (<Grid container>
    <Grid item md={11} style={{borderLeft: '1px solid #999999'}}>
      <Grid container style={{borderBottom: 'solid 0px #999999'}}>
        <Grid item md={11}>
        <List component={"ul"} ref={scrollRef} style={{maxHeight: 200, overflow: 'auto'}} className={classes.root}>
          {props.taskLogs?.log_lines?.map((row) => {
            return <li style={{marginLeft: 10}} key={row + uuid()}>{row}</li>;
          })}
        </List>
        </Grid>
      </Grid>
    </Grid>
  </Grid>);
}