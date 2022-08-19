import { Box, Button, Divider, Grid } from '@material-ui/core';
import React from 'react';
import { fetchWorkflowTasks } from './WorkflowTable.service';
import { useDispatch, useSelector } from 'react-redux';
import RefreshButton from '../../../components/CollapsedTable/RefreshButton';
import StatusIndicator from '../../../components/StatusIndicator';
import TaskList from './TaskList';
import { RootState } from '../../../store';
import { selectWorkflowPage, selectWorkflowTasksPerPage } from './WorkflowTable.reducer';

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
  const { namespace, workflowId, status } = props;
  const searchTerm = "";
  const workflowPage = useSelector((state: RootState) => selectWorkflowPage(state, workflowId));
  const tasksPerPage = useSelector((state: RootState) => selectWorkflowTasksPerPage(state, workflowId));
  const dispatch = useDispatch();

  const handleStop = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onStop?.(props.workflowId, props.namespace);
  const handleAbort = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onAbort?.(props.workflowId, props.namespace);
  const handleRestart = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => props.onRestart?.(props.workflowId, props.namespace);
  
  return (
    <div>
      <Divider variant="middle" component="div" light/>
      <Grid container spacing={0} justifyContent="flex-start" wrap="wrap" alignItems="flex-start" direction="row" style={{marginTop: 20, marginBottom: 0}}>
        <Box p={0} display="flex" style={{width: '100%'}}>
          <Box p={1} flexGrow={1}><StatusIndicator status={status}/></Box>
          <Box p={1}><Divider orientation="vertical" variant="fullWidth" style={{height: '100%' }}/></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleStop} disabled={status !== 'Running'}>Stop</Button></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleAbort} disabled={status !== 'Running'}>Abort</Button></Box>
          <Box p={1}><Button variant="contained" color="primary" size="small" onClick={handleRestart}>Restart</Button></Box>
          <Box p={1}>
            <RefreshButton onRefresh={() => dispatch(fetchWorkflowTasks(namespace, workflowId, searchTerm, workflowPage, tasksPerPage, "created_date", "asc"))}/>
          </Box>
        </Box>
        <Divider variant="inset" style={{width: '25%', marginLeft: 'auto', marginRight: '0'}} component="hr" orientation="horizontal"/>
        <Divider variant="fullWidth" component="hr" orientation="horizontal"/>
        <Divider variant="fullWidth" component="hr" orientation="horizontal"/>
        <Grid container direction="row">
          <Grid item md={1}></Grid>
          <Grid item md={11} style={{ flexShrink: 1, wordWrap: 'break-word' }}>
            <TaskList searchTerm={searchTerm} workflowId={workflowId} namespace={namespace}/>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}

export default WorkflowSubTable;
