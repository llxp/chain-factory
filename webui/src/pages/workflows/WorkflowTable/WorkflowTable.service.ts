import { ThunkAction } from "@reduxjs/toolkit";
import { RootState } from "../../../store";
import { PagedWorkflowTasks, PagedListItemType, HandleWorkflowResponse } from "./models";
import { handleWorkflow as handleWorkflowAPI, taskLogs, workflows, workflowStatus, workflowTasks } from "../../../api";
import { setTaskLogs, setTaskLogsError, setWorkflows, setWorkflowsError, setWorkflowsFetching, setWorkflowTasks, setWorkflowTasksError, setWorkflowTasksFetching, updateTaskStatus, updateWorkflowStatus } from "./WorkflowTable.reducer";
import { workflowsToListItemType } from "./utils";

export function fetchWorkflows(
  namespace: string,
  page: number,
  rowsPerPage: number,
  searchTerm: string,
  sortBy: string,
  sortOrder: string
): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      dispatch(setWorkflowsFetching(true));
      dispatch(setWorkflowsError(""));
      const workflowResult = await workflows(namespace, searchTerm, page, rowsPerPage, sortBy, sortOrder);
      dispatch(setWorkflows(workflowsToListItemType(workflowResult)));
      dispatch(setWorkflowsFetching(false));
    } catch (error) {
      console.log(error);
      dispatch(setWorkflows({} as PagedListItemType));
      dispatch(setWorkflowsFetching(false));
      dispatch(setWorkflowsError(error as string));
    }
  };
}

export function updateWorkflows(
  namespace: string,
  page: number,
  rowsPerPage: number,
  searchTerm: string,
  sortBy: string,
  sortOrder: string
): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      const workflowResult = await workflows(namespace, searchTerm, page, rowsPerPage, sortBy, sortOrder);
      dispatch(setWorkflows(workflowsToListItemType(workflowResult)));
    } catch (error) {
      console.log(error);
      dispatch(setWorkflows({} as PagedListItemType));
      dispatch(setWorkflowsError(error as string));
    }
  };
}

export function fetchWorkflowStatus(namespace: string, workflowIds: string | string[]): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    const workflowStatusResult = await workflowStatus(namespace, workflowIds);
    if (workflowStatusResult) {
      for (const workflowStatus of workflowStatusResult) {
        const workflowId = workflowStatus.workflow_id;
        dispatch(updateWorkflowStatus({workflowId: workflowId, status: workflowStatus.status}));
        dispatch(updateTaskStatus({workflowId: workflowId, status: workflowStatus.tasks}));
      }
    }
  }
}

export function fetchWorkflowTasks(
  namespace: string,
  workflowId: string,
  searchTerm: string,
  page: number,
  rowsPerPage: number,
  sortBy: string,
  sortOrder: string
): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    dispatch(setWorkflowTasksFetching(true));
    try {
      const workflowTasksResult = await workflowTasks(namespace, workflowId, searchTerm, page, rowsPerPage, sortBy, sortOrder);
      dispatch(setWorkflowTasks({workflowId: workflowId, workflowTasks: workflowTasksResult}));
      dispatch(setWorkflowTasksFetching(false));
      dispatch(setWorkflowTasksError(false));
    } catch (error) {
      console.log(error);
      dispatch(setWorkflowTasks({workflowId: workflowId, workflowTasks: {} as PagedWorkflowTasks}));
      dispatch(setWorkflowTasksError(true));
      dispatch(setWorkflowTasksFetching(false));
    }
  };
}

export function fetchTaskLogs(
  namespace: string,
  page: number,
  rowsPerPage: number,
  searchTerm: string,
  taskId: string
): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      dispatch(setTaskLogsError(""));
      const taskLogsResult = await taskLogs(namespace, taskId, searchTerm, page, rowsPerPage);
      dispatch(setTaskLogs({ taskId: taskId, taskLogs: taskLogsResult }));
      dispatch(setTaskLogsError(""));
    } catch (error) {
      console.log(error);
      dispatch(setTaskLogsError(error as string));
    }
  };
}

export function handleWorkflow(
  namespace: string,
  workflowId: string,
  action: string
): ThunkAction<Promise<HandleWorkflowResponse>, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      return await handleWorkflowAPI(namespace, action, workflowId);
    } catch (error) {
      console.log(error);
      return { status: "error" };
    }
  }
}
