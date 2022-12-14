import { Action, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { nodeMetrics, workflowMetrics } from "../../api";
import { NodeMetricsResponse } from "../../models";
import { RootState } from '../../store';
import { WorkflowMetrics } from "../workflows/WorkflowTable/models";
import { setAllNodes, setAllWorkflows, setRunningNodes, setRunningWorkflows, setStoppedNodes, setStoppedWorkflows } from "./Dashboard.reducer";

export function fetchNodeMetrics(namespace: string): ThunkAction<void, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      const nodeMetricsResponse = await nodeMetrics(namespace);
      const nodeMetricsResult = nodeMetricsResponse as NodeMetricsResponse[];
      const allNodes = nodeMetricsResult.map((node) => node.node_name);
      dispatch(setAllNodes(allNodes));
      dispatch(setRunningNodes(nodeMetricsResult.filter((node) => node.active).map((node) => node.node_name)));
      dispatch(setStoppedNodes(nodeMetricsResult.filter((node) => !node.active).map((node) => node.node_name)));
    } catch (error) {
      console.log(error);
      dispatch(setAllNodes([]));
      dispatch(setRunningNodes([]));
      dispatch(setStoppedNodes([]));
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