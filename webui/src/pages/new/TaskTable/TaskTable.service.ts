import { Action, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { RootState } from '../../../store';
import { PagedListItemType, PagedNodeTasks } from "./models";
import { activeTasks, startTask as startTaskApi } from '../../../api';
import { nodeTasksToTaskNodes, tasksToListItemTypes } from "./utils";
import { setRegisteredTasks, setRegisteredTasksError, setRegisteredTasksFetching } from "./TaskTable.reducer";
import { HandleWorkflowResponse } from "../../workflows/WorkflowTable/models";

export function fetchAvailableTasks(namespace: string, page: number, rowsPerPage: number, searchTerm: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      dispatch(setRegisteredTasksFetching(true));
      dispatch(setRegisteredTasksError(""));
      const activeTasksResult = await activeTasks(namespace, searchTerm, page, rowsPerPage);
      const taskNodes = nodeTasksToTaskNodes(activeTasksResult as PagedNodeTasks);
      const listItems = tasksToListItemTypes(taskNodes);
      dispatch(setRegisteredTasks(listItems));
      dispatch(setRegisteredTasksFetching(false));
    } catch (error: any) {
      console.log(error);
      dispatch(setRegisteredTasksFetching(false));
      dispatch(setRegisteredTasksError(error.toString() as string));
      dispatch(setRegisteredTasks({} as PagedListItemType));
    }
  };
}

export function updateAvailableTasks(namespace: string, page: number, rowsPerPage: number, searchTerm: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      const activeTasksResult = await activeTasks(namespace, searchTerm, page, rowsPerPage);
      const taskNodes = nodeTasksToTaskNodes(activeTasksResult as PagedNodeTasks);
      const listItems = tasksToListItemTypes(taskNodes);
      dispatch(setRegisteredTasks(listItems));
    } catch (error: any) {
      console.log(error);
      dispatch(setRegisteredTasks({} as PagedListItemType));
      dispatch(setRegisteredTasksError(error.toString() as string));
    }
  };
}

export function startTask(namespace, task, taskArguments, tags): ThunkAction<Promise<HandleWorkflowResponse>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    return await startTaskApi(namespace, task, taskArguments, tags) as HandleWorkflowResponse;
  };
}