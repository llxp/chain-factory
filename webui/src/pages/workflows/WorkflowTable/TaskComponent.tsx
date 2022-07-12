import { Avatar, CircularProgress, Grid, ListItem, ListItemAvatar, ListItemText, Theme, Typography } from "@material-ui/core";
import { createStyles, makeStyles } from "@material-ui/styles";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectNamespace } from "../../core/toolbar/NamespaceSelector/NamespaceSelector.reducer";
import { getbackgroundColor } from "./utils";
import { fetchTaskLogs } from "./WorkflowTable.service";
import { selectTaskLogs, selectTaskLogsError, selectTaskLogsFetching } from "./WorkflowTable.reducer";
import TaskLog from "./TaskLog";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    inline: {
      display: 'inline',
    },
  }),
);

export interface ITaskComponentProps {
  taskId: string;
  args: any;
  name: string;
  createdDate: string;
  searchTerm: string;
  status: string;
}

export default function TaskComponent(props: ITaskComponentProps) {
  const {taskId, args, name, createdDate, searchTerm, status} = props;
  const classes = useStyles();
  const dispatch = useDispatch();
  const namespace = useSelector(selectNamespace);
  const page = 0;
  const rowsPerPage = 99999;

  const taskLogs = useSelector(selectTaskLogs);
  const taskLogsFetching = useSelector(selectTaskLogsFetching);
  const taskLogsError = useSelector(selectTaskLogsError);


  useEffect(() => {
    if (taskLogsFetching || taskLogsError || !namespace) {
      //|| (taskLogs[taskId] && status !== 'RUNNING')) {
      return;
    }
    dispatch(fetchTaskLogs(namespace, page, rowsPerPage, searchTerm, taskId));
    const interval = setInterval(() => {
      if (taskLogsFetching || taskLogsError || !namespace || status !== 'RUNNING') {
        clearInterval(interval);
        return;
      }
      dispatch(fetchTaskLogs(namespace, page, rowsPerPage, searchTerm, taskId));
    }, 5000);
    return () => clearInterval(interval);
  }, [taskLogsFetching, taskLogsError, namespace, page, rowsPerPage, taskId, searchTerm, status, dispatch]);

  if (taskLogsFetching) {
    return <CircularProgress/>;
  }

  const currentTaskLogs = taskLogs ? taskLogs[taskId] : null;

  if (taskLogsError) {
    return (
      <div>
        <Typography color="error">
          <span>{taskLogsError}</span>
        </Typography>
      </div>
    );
  }

  const style={};
  if (status !== undefined && status) {
    style['backgroundColor'] = getbackgroundColor(status);
  }

  return (<div style={{marginBottom: 20}}>
    <ListItem alignItems="flex-start" style={{borderLeft: 'solid 1px #999999'}}>
      <ListItemAvatar>
        <Avatar alt={(status ? status: "")} style={style} src="/static/images/avatar/1.jpg"/>
      </ListItemAvatar>
      <ListItemText
        primary={new Date(createdDate).toLocaleString()}
        secondaryTypographyProps={{component: 'span'}}
        secondary={
          <React.Fragment>
            <Grid container>
              <Grid item md={1}>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  Name:
                </Typography>
              </Grid>
              <Grid item md>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  {name}
                </Typography>
              </Grid>
            </Grid>
            <Grid container>
              <Grid item md={1}>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  Arguments:
                </Typography>
              </Grid>
              <Grid item md>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  {JSON.stringify(args) }
                </Typography>
              </Grid>
            </Grid>
            <Grid container>
              <Grid item md={1}>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  Status:
                </Typography>
              </Grid>
              <Grid item md>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  {status ? status : ""}
                </Typography>
              </Grid>
            </Grid>
            <div style={{marginTop: '10px', width: '50%', borderBottom: '1px solid #999999'}}/>
            <Grid container>
              <Grid item md={1}>
                <Typography component="span" variant="body2" className={classes.inline} color="textPrimary">
                  Logs:
                </Typography>
              </Grid>
            </Grid>
          </React.Fragment>
        }
      />
    </ListItem>
    <TaskLog taskLogs={currentTaskLogs}/>
  </div>)
};