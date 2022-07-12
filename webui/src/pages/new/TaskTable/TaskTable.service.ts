import { ThunkAction } from "@reduxjs/toolkit";
import { RootState } from '../../../store';
import { PagedListItemType } from "./models";
import { activeTasks, startTask as startTaskApi } from '../../../api';
import { nodeTasksToTaskNodes, tasksToListItemTypes } from "./utils";
import { setRegisteredTasks, setRegisteredTasksError, setRegisteredTasksFetching } from "./TaskTable.reducer";
import { HandleWorkflowResponse } from "../../workflows/WorkflowTable/models";

export function fetchAvailableTasks(namespace: string, page: number, rowsPerPage: number, searchTerm: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      dispatch(setRegisteredTasksFetching(true));
      dispatch(setRegisteredTasksError(""));
      const activeTasksResult = await activeTasks(namespace, searchTerm, page, rowsPerPage);
      const taskNodes = nodeTasksToTaskNodes(activeTasksResult);
      const listItems = tasksToListItemTypes(taskNodes);
      dispatch(setRegisteredTasks(listItems));
      dispatch(setRegisteredTasksFetching(false));
    } catch (error) {
      console.log(error);
      dispatch(setRegisteredTasksFetching(false));
      dispatch(setRegisteredTasksError(error.toString()));
      dispatch(setRegisteredTasks({} as PagedListItemType));
    }
  };
}

export function updateAvailableTasks(namespace: string, page: number, rowsPerPage: number, searchTerm: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch, getState) => {
    try {
      const activeTasksResult = await activeTasks(namespace, searchTerm, page, rowsPerPage);
      const taskNodes = nodeTasksToTaskNodes(activeTasksResult);
      const listItems = tasksToListItemTypes(taskNodes);
      dispatch(setRegisteredTasks(listItems));
    } catch (error) {
      console.log(error);
      dispatch(setRegisteredTasks({} as PagedListItemType));
      dispatch(setRegisteredTasksError(error.toString()));
    }
  };
}

export function startTask(namespace, node, task, taskArguments, tags): ThunkAction<Promise<HandleWorkflowResponse>, RootState, undefined, any> {
  return async (dispatch, getState) => {
    return await startTaskApi(namespace, node, task, taskArguments, tags);
  };
}