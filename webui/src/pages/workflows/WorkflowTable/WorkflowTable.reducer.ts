import { createSelector, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { DefaultRootState } from "react-redux";
import { RootState } from "../../../store";
import { PagedListItemType, PagedTaskLogs, PagedWorkflowTasks, TaskStatus } from "./models";

// State definition
interface WorkflowsState {
  workflows: PagedListItemType;
  workflowsFetching: boolean;
  workflowsError: string;
  workflowDetailsOpened: string[];
  workflowsSortBy: string;
  workflowsSortOrder: string;
  workflowsSearch: string;
  workflowsPage: number;
  workflowsPerPage: number;
  workflowTasks: { [key: string]: PagedWorkflowTasks };
  workflowTasksFetching: boolean;
  workflowTasksError: boolean;
  taskLogs: { [key: string]: PagedTaskLogs };
  taskLogsFetching: boolean;
  taskLogsError: string;
  selectedWorkflows: string[];
  tasksPages: { [key: string]: number };
  workflowTasksPerPage: { [key: string]: number };
}

// Initial state
const initialState: WorkflowsState = {
  workflows: { items: [], totalCount: 0} as PagedListItemType,
  workflowsFetching: false,
  workflowsError: "",
  workflowDetailsOpened: [] as string[],
  workflowsSortBy: "created_date",
  workflowsSortOrder: "desc",
  workflowsSearch: "",
  workflowsPage: 0,
  workflowsPerPage: 10,
  workflowTasks: {} as { [key: string]: PagedWorkflowTasks },
  workflowTasksFetching: false,
  workflowTasksError: false,
  taskLogs: {} as { [key: string]: PagedTaskLogs },
  taskLogsFetching: false,
  taskLogsError: "",
  selectedWorkflows: [] as string[],
  tasksPages: {} as { [key: string]: number },
  workflowTasksPerPage: {} as { [key: string]: number },
};

// Slice Definition
export const workflowsSlice = createSlice({
  name: "workflows",
  initialState,
  reducers: {
    setWorkflows: (state, action: PayloadAction<PagedListItemType>) => {
      if (action.payload.totalCount === 0 || action.payload.totalCount === undefined) {
        console.log("no workflows fetched");
        return;
      }
      if (state.workflows.items === undefined) {
        state.workflows.items = [];
      }
      state.workflows.items = [];
      for (const workflow of action.payload.items) {
        const oldWorkflow = state.workflows.items[workflow.workflowId];
        if (oldWorkflow?.status !== workflow?.status) {
          let index = state.workflows.items.indexOf(oldWorkflow);
          if (index === -1) {
            state.workflows.items.push(workflow);
          } else {
            state.workflows.items[index] = workflow;
          }
        }
      }
      state.workflows.totalCount = action.payload.totalCount;
    },
    updateWorkflowStatus: (state, action: PayloadAction<{workflowId: string, status: string}>) => {
      const workflow = state.workflows.items.find(workflow => workflow.workflowId === action.payload.workflowId);
      if (workflow) {
        let index = state.workflows.items.indexOf(workflow);
        if (index !== -1) {
          state.workflows.items[index].status = action.payload.status;
        }
      }
    },
    updateTaskStatus: (state, action: PayloadAction<{workflowId: string, status: TaskStatus[]}>) => {
      if (!state.workflowTasks[action.payload.workflowId] || !state.workflowTasks[action.payload.workflowId].tasks) {
        state.workflowTasks[action.payload.workflowId] = {
          tasks: [],
          total_count: 0,
          count: 0
        };
      }
      if (state.workflowTasks && state.workflowTasks[action.payload.workflowId]) {
        state.workflowTasks[action.payload.workflowId]?.tasks.forEach(task => {
          action.payload.status.forEach(status => {
            if (task.task_id === status.task_id) {
              task.status = status.status;
            }
          });
        });
      }
    },
    clearWorkflows: (state) => {
      state.workflows.items = [];
      state.workflows.totalCount = 0;
    },
    setWorkflowsFetching: (state, action: PayloadAction<boolean>) => {
      state.workflowsFetching = action.payload;
    },
    setWorkflowsError: (state, action: PayloadAction<string>) => {
      state.workflowsError = action.payload;
    },
    setWorkflowDetailsOpened: (state, action: PayloadAction<string[]>) => {
      state.workflowDetailsOpened = action.payload;
    },
    setWorkflowsSortBy: (state, action: PayloadAction<string>) => {
      state.workflowsSortBy = action.payload;
    },
    setWorkflowsSortOrder: (state, action: PayloadAction<string>) => {
      state.workflowsSortOrder = action.payload;
    },
    setWorkflowsSearch: (state, action: PayloadAction<string>) => {
      state.workflowsSearch = action.payload;
    },
    setWorkflowsPage: (state, action: PayloadAction<number>) => {
      state.workflowsPage = action.payload;
    },
    setWorkflowsPerPage: (state, action: PayloadAction<number>) => {
      state.workflowsPerPage = action.payload;
    },
    setWorkflowTasks: (state, action: PayloadAction<{ workflowId: string, workflowTasks: PagedWorkflowTasks }>) => {
      if (state.workflowTasks) {
        state.workflowTasks[action.payload.workflowId] = action.payload.workflowTasks;
      } else {
        state.workflowTasks = {};
        state.workflowTasks[action.payload.workflowId] = action.payload.workflowTasks;
      }
    },
    setWorkflowTasksFetching: (state, action: PayloadAction<boolean>) => {
      state.workflowTasksFetching = action.payload;
    },
    setWorkflowTasksError: (state, action: PayloadAction<boolean>) => {
      state.workflowTasksError = action.payload;
    },
    setTaskLogs: (state, action: PayloadAction<{ taskId: string, taskLogs: PagedTaskLogs }>) => {
      if (state.taskLogs) {
        state.taskLogs[action.payload.taskId] = action.payload.taskLogs;
      } else {
        state.taskLogs = {};
        state.taskLogs[action.payload.taskId] = action.payload.taskLogs;
      }
    },
    setTaskLogsFetching: (state, action: PayloadAction<boolean>) => {
      state.taskLogsFetching = action.payload;
    },
    setTaskLogsError: (state, action: PayloadAction<string>) => {
      state.taskLogsError = action.payload;
    },
    setSelectedWorkflows: (state, action: PayloadAction<string[]>) => {
      state.selectedWorkflows = action.payload;
    },
    setWorkflowPage: (state, action: PayloadAction<{ workflowId: string, page: number }>) => {
      if (state.tasksPages) {
        state.tasksPages[action.payload.workflowId] = action.payload.page;
      } else {
        state.tasksPages = {};
        state.tasksPages[action.payload.workflowId] = action.payload.page;
      }
    },
    setWorkflowTasksPerPage: (state, action: PayloadAction<{ workflowId: string, perPage: number }>) => {
      if (state.workflowTasksPerPage) {
        state.workflowTasksPerPage[action.payload.workflowId] = action.payload.perPage;
      } else {
        state.workflowTasksPerPage = {};
        state.workflowTasksPerPage[action.payload.workflowId] = action.payload.perPage;
      }
    }
  },
});

// export reducers
export const { setWorkflows } = workflowsSlice.actions;
export const { updateWorkflowStatus } = workflowsSlice.actions;
export const { updateTaskStatus } = workflowsSlice.actions;
export const { clearWorkflows } = workflowsSlice.actions;
export const { setWorkflowsFetching } = workflowsSlice.actions;
export const { setWorkflowsError } = workflowsSlice.actions;
export const { setWorkflowDetailsOpened } = workflowsSlice.actions;
export const { setWorkflowsSortBy } = workflowsSlice.actions;
export const { setWorkflowsSortOrder } = workflowsSlice.actions;
export const { setWorkflowsSearch } = workflowsSlice.actions;
export const { setWorkflowsPage } = workflowsSlice.actions;
export const { setWorkflowsPerPage } = workflowsSlice.actions;
export const { setWorkflowTasks } = workflowsSlice.actions;
export const { setWorkflowTasksFetching } = workflowsSlice.actions;
export const { setWorkflowTasksError } = workflowsSlice.actions;
export const { setTaskLogs } = workflowsSlice.actions;
export const { setTaskLogsFetching } = workflowsSlice.actions;
export const { setTaskLogsError } = workflowsSlice.actions;
export const { setSelectedWorkflows } = workflowsSlice.actions;
export const { setWorkflowPage } = workflowsSlice.actions;

export const selectWorkflows = (state: RootState) => state.workflows.workflows;
export const selectWorkflowsFetching = (state: RootState) => state.workflows.workflowsFetching;
export const selectWorkflowsError = (state: RootState) => state.workflows.workflowsError;
export const selectWorkflowDetailsOpened = (state: RootState) => state.workflows.workflowDetailsOpened;
export const selectWorkflowsSortBy = (state: RootState) => state.workflows.workflowsSortBy;
export const selectWorkflowsSortOrder = (state: RootState) => state.workflows.workflowsSortOrder;
export const selectWorkflowsSearch = (state: RootState) => state.workflows.workflowsSearch;
export const selectWorkflowsPage = (state: RootState) => state.workflows.workflowsPage;
export const selectWorkflowsPerPage = (state: RootState) => state.workflows.workflowsPerPage;
export const selectWorkflowTasks = (state: RootState, workflowId: string) => state.workflows.workflowTasks[workflowId] || { total_count: 0, tasks: [], count: 0 };
export const selectWorkflowTasksFetching = (state: RootState) => state.workflows.workflowTasksFetching;
export const selectWorkflowTasksError = (state: RootState) => state.workflows.workflowTasksError;
export const selectTaskLogs = (state: RootState) => state.workflows.taskLogs;
export const selectTaskLogsFetching = (state: RootState) => state.workflows.taskLogsFetching;
export const selectTaskLogsError = (state: RootState) => state.workflows.taskLogsError;
export const selectSelectedWorkflows = (state: RootState) => state.workflows.selectedWorkflows;
export const selectTasksPages = (state: RootState) => state.workflows.tasksPages;
export const selectWorkflowPage = (state: RootState, workflowId: string) => state.workflows.tasksPages[workflowId] || 1;
export const selectWorkflowTasksCount = (state: RootState, workflowId: string) => state.workflows.workflowTasks[workflowId] ? state.workflows.workflowTasks[workflowId].total_count : 0;
export const selectWorkflowTasksPerPage = (state: RootState, workflowId: string) => state.workflows.workflowTasksPerPage[workflowId] || 1;

export const WorkflowsSlice = workflowsSlice.reducer;
