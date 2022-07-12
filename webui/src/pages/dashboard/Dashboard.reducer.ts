import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../store";
import { WorkflowMetrics } from "../workflows/WorkflowTable/models";

// State definition
interface DashboardState {
  allNodes: string[];
  runningNodes: string[];
  stoppedNodes: string[];
  allWorkflows: { [key: string]: WorkflowMetrics[] };
  runningWorkflows: { [key: string]: WorkflowMetrics[] };
  stoppedWorkflows: { [key: string]: WorkflowMetrics[] };
}

// Initial state
const initialState: DashboardState = {
  allNodes: [],
  runningNodes: [],
  stoppedNodes: [],
  allWorkflows: {} as { [key: string]: WorkflowMetrics[] },
  runningWorkflows: {} as { [key: string]: WorkflowMetrics[] },
  stoppedWorkflows: {} as { [key: string]: WorkflowMetrics[] },
};

// Slice Definition
export const dashboardSlice = createSlice({
  name: "dashboard",
  initialState,
  reducers: {
    setAllNodes: (state, action: PayloadAction<string[]>) => {
      state.allNodes = action.payload;
    },
    setRunningNodes: (state, action: PayloadAction<string[]>) => {
      state.runningNodes = action.payload;
    },
    setStoppedNodes: (state, action: PayloadAction<string[]>) => {
      state.stoppedNodes = action.payload;
    },
    setAllWorkflows: (state, action: PayloadAction<{ [key: string]: WorkflowMetrics[] }>) => {
      state.allWorkflows = action.payload;
    },
    setRunningWorkflows: (state, action: PayloadAction<{ [key: string]: WorkflowMetrics[] }>) => {
      state.runningWorkflows = action.payload;
    },
    setStoppedWorkflows: (state, action: PayloadAction<{ [key: string]: WorkflowMetrics[] }>) => {
      state.stoppedWorkflows = action.payload;
    }
  },
});

// export reducers
export const {
  setAllNodes,
  setRunningNodes,
  setStoppedNodes,
  setAllWorkflows,
  setRunningWorkflows,
  setStoppedWorkflows
} = dashboardSlice.actions;

export const selectAllNodes = (state: RootState) => state.dashboard.allNodes;
export const selectRunningNodes = (state: RootState) => state.dashboard.runningNodes;
export const selectStoppedNodes = (state: RootState) => state.dashboard.stoppedNodes;
export const selectAllWorkflows = (state: RootState) => state.dashboard.allWorkflows;
export const selectRunningWorkflows = (state: RootState) => state.dashboard.runningWorkflows;
export const selectStoppedWorkflows = (state: RootState) => state.dashboard.stoppedWorkflows;

export const DashboardSlice = dashboardSlice.reducer;
