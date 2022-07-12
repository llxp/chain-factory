import { createStyles, makeStyles } from "@material-ui/styles";
import React from "react";
import { PagedWorkflowTasks } from "./models";
import TaskComponent from "./TaskComponent";
import uuid from 'react-uuid';
import { Theme, List } from "@material-ui/core";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
      backgroundColor: theme.palette.background.paper,
    }
  }),
);

export interface TaskListProps {
  tasks: PagedWorkflowTasks;
  searchTerm: string;
};

export default function TaskList(props: TaskListProps) {
  const classes = useStyles();
  return (<List key={uuid()} className={classes.root}>
    {(props.tasks?.tasks || []).map((task) => {
      return (
        <TaskComponent
          key={uuid() + task.task_id}
          taskId={task.task_id}
          args={task.arguments}
          name={task.name}
          createdDate={task.received_date}
          searchTerm={props.searchTerm}
          status={task.status || "Pending"}
        />
      );
    })}
  </List>);
}