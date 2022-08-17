import { Action, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { nodeMetrics, workflowMetrics } from "../../api";
import { RootState } from '../../store';
import { WorkflowMetrics } from "../workflows/WorkflowTable/models";
import { setAllNodes, setAllWorkflows, setRunningNodes, setRunningWorkflows, setStoppedNodes, setStoppedWorkflows } from "./Dashboard.reducer";

export function fetchNodeMetrics(namespace: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      const nodeMetricsResult = await nodeMetrics(namespace);
      dispatch(setAllNodes(Object.keys(nodeMetricsResult)));
      dispatch(setRunningNodes(Object.keys(nodeMetricsResult).filter(node => nodeMetricsResult[node] === true)));
      dispatch(setStoppedNodes(Object.keys(nodeMetricsResult).filter(node => nodeMetricsResult[node] === false)));
    } catch (error) {
      console.log(error);
    }
  };
}

export function fetchWorkflowMetrics(namespace: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      const workflowMetricsResult = await workflowMetrics(namespace);
      const workflowsPerDay = (workflowMetricsResult as WorkflowMetrics[]).reduce((prev, curr) => {
        const date = new Date(curr.created_date).toDateString();
        if (!prev[date]) {
          prev[date] = [];
        }
        prev[date].push(curr);
        return prev;
      }, {});
      dispatch(setAllWorkflows(workflowsPerDay));
      const runningWorkflowsPerDay = (workflowMetricsResult as WorkflowMetrics[]).reduce((prev, curr) => {
        if (curr.status === "Exception" || curr.status === "Failed") {
          const date = new Date(curr.created_date).toDateString();
          if (!prev[date]) {
            prev[date] = [];
          }
          prev[date].push(curr);
          return prev;
        }
        return prev;
      }, {});
      dispatch(setRunningWorkflows(runningWorkflowsPerDay));
      const stoppedWorkflowsPerDay = (workflowMetricsResult as WorkflowMetrics[]).reduce((prev, curr) => {
        if (curr.status === "Failed" || curr.status === "Timeout") {
          const date = new Date(curr.created_date).toDateString();
          if (!prev[date]) {
            prev[date] = [];
          }
          prev[date].push(curr);
          return prev;
        }
        return prev;
      }, {});
      dispatch(setStoppedWorkflows(stoppedWorkflowsPerDay));
    } catch (error) {
      console.log(error);
    }
  };
}