import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../../store";
import { PagedListItemType } from "./models";

// State definition
interface WorkflowsState {
  registeredTasks: PagedListItemType;
  registeredTasksFetching: boolean;
  registeredTasksError: string;
  taskDetailsOpened: string[];
  tasksSortBy: string;
  tasksSortOrder: string;
  tasksSearch: string;
  tasksPage: number;
  tasksPerPage: number;
  selectedTasks: string[];
}

// Initial state
const initialState: WorkflowsState = {
  registeredTasks: {} as PagedListItemType,
  registeredTasksFetching: false,
  registeredTasksError: "",
  taskDetailsOpened: [],
  tasksSortBy: "name",
  tasksSortOrder: "desc",
  tasksSearch: "",
  tasksPage: 0,
  tasksPerPage: 10,
  selectedTasks: []
};

// Slice Definition
export const tasksSlice = createSlice({
  name: "tasks",
  initialState,
  reducers: {
    setRegisteredTasks: (state, action: PayloadAction<PagedListItemType>) => {
      state.registeredTasks = action.payload;
    },
    clearRegisteredTasks: (state, action: PayloadAction<void>) => {
      state.registeredTasks = {} as PagedListItemType;
    },
    setRegisteredTasksFetching: (state, action: PayloadAction<boolean>) => {
      state.registeredTasksFetching = action.payload;
    },
    setRegisteredTasksError: (state, action: PayloadAction<string>) => {
      state.registeredTasksError = action.payload;
    },
    setTaskDetailsOpened: (state, action: PayloadAction<string[]>) => {
      state.taskDetailsOpened = action.payload;
    },
    setTasksSortBy: (state, action: PayloadAction<string>) => {
      state.tasksSortBy = action.payload;
    },
    setTasksSortOrder: (state, action: PayloadAction<string>) => {
      state.tasksSortOrder = action.payload;
    },
    setTasksSearch: (state, action: PayloadAction<string>) => {
      state.tasksSearch = action.payload;
    },
    setTasksPage: (state, action: PayloadAction<number>) => {
      state.tasksPage = action.payload;
    },
    setTasksPerPage: (state, action: PayloadAction<number>) => {
      state.tasksPerPage = action.payload;
    },
    setSelectedTasks: (state, action: PayloadAction<string[]>) => {
      state.selectedTasks = action.payload;
    }
  },
});

// export reducers
export const {
  setRegisteredTasks,
  clearRegisteredTasks,
  setRegisteredTasksFetching,
  setRegisteredTasksError,
  setTaskDetailsOpened,
  setTasksSortBy,
  setTasksSortOrder,
  setTasksSearch,
  setTasksPage,
  setTasksPerPage,
  setSelectedTasks
} = tasksSlice.actions;

export const selectRegisteredTasks = (state: RootState) => state.tasks.registeredTasks;
export const selectRegisteredTasksFetching = (state: RootState) => state.tasks.registeredTasksFetching;
export const selectRegisteredTasksError = (state: RootState) => state.tasks.registeredTasksError;
export const selectTaskDetailsOpened = (state: RootState) => state.tasks.taskDetailsOpened;
export const selectTasksSortBy = (state: RootState) => state.tasks.tasksSortBy;
export const selectTasksSortOrder = (state: RootState) => state.tasks.tasksSortOrder;
export const selectTasksSearch = (state: RootState) => state.tasks.tasksSearch;
export const selectTasksPage = (state: RootState) => state.tasks.tasksPage;
export const selectTasksPerPage = (state: RootState) => state.tasks.tasksPerPage;
export const selectSelectedTasks = (state: RootState) => state.tasks.selectedTasks;

export const TasksSlice = tasksSlice.reducer;
