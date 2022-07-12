import { Box, Button, CircularProgress, Divider, Grid } from '@material-ui/core';
import React, { useEffect } from 'react';
import { fetchWorkflowTasks } from './WorkflowTable.service';
import { useDispatch, useSelector } from 'react-redux';
import RefreshButton from '../../../components/CollapsedTable/RefreshButton';
import { selectWorkflowTasks, selectWorkflowTasksError, selectWorkflowTasksFetching } from './WorkflowTable.reducer';
import StatusIndicator from '../../../components/StatusIndicator';
import TaskList from './TaskList';

export interface IWorkflowSubTableProps {
  onStop?: (
      workflowId: string,
      namespace: string
    ) => void;
  onAbort?: (
    workflowId: string,
    namespace: string
  ) => void;
  onRestart?: (
    workflowId: string,
    namespace: string
  ) => void;
  workflowId: string;
  namespace: string;
  status: string;
}

export function WorkflowSubTable(props: IWorkflowSubTableProps) {
  const searchTerm = "";
  const workflowTasks = useSelector(selectWorkflowTasks);
  const workflowTasksFetching = useSelector(selectWorkflowTasksFetching);
  const workflowTasksError = useSelector(selectWorkflowTasksError);
  const dispatch = useDispatch();

  useEffect(() => {
    //dispatch(fetchWorkflowStatus(props.namespace, props.workflowId));
    dispatch(fetchWorkflowTasks(props.namespace, props.workflowId, searchTerm, 0, 10000, "created_date", "asc"));
  }, [searchTerm, props, dispatch]);

  const handleStop = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onStop?.(props.workflowId, props.namespace);
  const handleAbort = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onAbort?.(props.workflowId, props.namespace);
  const handleRestart = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onRestart?.(props.workflowId, props.namespace);

  if (workflowTasksFetching) {
    return <CircularProgress/>;
  }

  if (!workflowTasks[props.workflowId] || workflowTasks[props.workflowId]?.total_count === 0 || workflowTasks === undefined || workflowTasksError) {
    return <div>No tasks</div>;
  }
  const currentWorkflowTasks = workflowTasks[props.workflowId];
  
  return (
    <div>
      <Divider variant="middle" component="div" light/>
      <Grid container spacing={0} justifyContent="flex-start" wrap="wrap" alignItems="flex-start" direction="row" style={{marginTop: 20, marginBottom: 0}}>
        <Box p={0} display="flex" style={{width: '100%'}}>
          <Box p={1} flexGrow={1}><StatusIndicator status={props.status}/></Box>
          <Box p={1}><Divider orientation="vertical" variant="fullWidth" style={{height: '100%' }}/></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleStop} disabled={props.status !== 'Running'}>Stop</Button></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleAbort} disabled={props.status !== 'Running'}>Abort</Button></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleRestart}>Restart</Button></Box>
          <Box p={1}>
            <RefreshButton onRefresh={() => { dispatch(fetchWorkflowTasks(props.namespace, props.workflowId, searchTerm, 0, 10000, "created_date", "asc"));}}/>
          </Box>
        </Box>
        <Divider variant="inset" style={{width: '25%', marginLeft: 'auto', marginRight: '0'}} component="hr" orientation="horizontal"/>
        <Divider variant="fullWidth" component="hr" orientation="horizontal"/>
        <Divider variant="fullWidth" component="hr" orientation="horizontal"/>
        <Grid container direction="row">
          <Grid item md={1}></Grid>
          <Grid item md={11} style={{ flexShrink: 1, wordWrap: 'break-word' }}>
            <TaskList tasks={currentWorkflowTasks} searchTerm={searchTerm}/>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}

export default WorkflowSubTable;
