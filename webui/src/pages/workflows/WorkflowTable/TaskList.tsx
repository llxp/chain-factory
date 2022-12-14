import { createStyles, makeStyles } from "@material-ui/styles";
import React, { useEffect } from "react";
import TaskComponent from "./TaskComponent";
import uuid from 'react-uuid';
import { Theme, List, CircularProgress } from "@material-ui/core";
import { useDispatch, useSelector } from "react-redux";
import { selectWorkflowPage, selectWorkflowTasks, selectWorkflowTasksCount, selectWorkflowTasksError, selectWorkflowTasksFetching, selectWorkflowTasksPerPage, setWorkflowPage } from "./WorkflowTable.reducer";
import { RootState } from "../../../store";
import { fetchWorkflowStatus, fetchWorkflowTasks } from "./WorkflowTable.service";
import { Pagination } from "@material-ui/lab";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
      backgroundColor: theme.palette.background.paper,
    }
  }),
);

export interface TaskListProps {
  searchTerm: string;
  workflowId: string;
  namespace: string;
};

export default function TaskList(props: TaskListProps) {
  const { workflowId, searchTerm, namespace } = props;
  const workflowPage = useSelector((state: RootState) => selectWorkflowPage(state, workflowId));
  const workflowTasks = useSelector((state: RootState) => selectWorkflowTasks(state, workflowId));
  const workflowTasksFetching = useSelector(selectWorkflowTasksFetching);
  const workflowTasksError = useSelector(selectWorkflowTasksError);
  const workflowTasksCount = useSelector((state: RootState) => selectWorkflowTasksCount(state, workflowId));
  const tasksPerPage = useSelector((state: RootState) => selectWorkflowTasksPerPage(state, workflowId));
  const dispatch = useDispatch();
  const classes = useStyles();

  useEffect(() => {
    dispatch(setWorkflowPage({workflowId: workflowId, page: 0}));
  }, [workflowId, dispatch]);

  useEffect(() => {
    dispatch(fetchWorkflowStatus(namespace, workflowId));
    dispatch(fetchWorkflowTasks(namespace, workflowId, searchTerm, workflowPage - 1, tasksPerPage, "created_date", "asc"));
  }, [searchTerm, namespace, workflowId, workflowPage, tasksPerPage, dispatch]);

  if (workflowTasksFetching) {
    return <CircularProgress/>;
  }

  if (workflowTasks.total_count === 0 || workflowTasksError) {
    return <div>No tasks</div>;
  }

  const workflowPages = Math.ceil(workflowTasksCount / tasksPerPage);

  return (<>
    <List key={uuid()} className={classes.root}>
      {(workflowTasks.tasks || []).map((task) => {
        return (
          <TaskComponent
            key={workflowId + task.task_id}
            taskId={task.task_id}
            args={task.arguments}
            name={task.name}
            createdDate={task.received_date}
            searchTerm={searchTerm}
            status={task.status || "Pending"}
            workflowId={workflowId}
          />
        );
      })}
    </List>
    <Pagination count={workflowPages} onChange={(event: React.ChangeEvent<unknown>, page: number) => {
      dispatch(setWorkflowPage({workflowId: workflowId, page: page}));
    }} page={workflowPage} showFirstButton showLastButton/>
  </>);
}