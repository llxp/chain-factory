import { Divider, Grid, List, Typography } from "@material-ui/core";
import React, { useEffect } from "react";
import Paper from '@material-ui/core/Paper';
import NumberIndicator from "../../components/Dashboard/NumberIndicator";
import PlotChart from "../../components/Dashboard/PlotChart";
import { fetchNodeMetrics, fetchWorkflowMetrics } from "./Dashboard.service";
import { useDispatch, useSelector } from "react-redux";
import { selectNamespace, selectNamespaceDisabled } from "../core/toolbar/NamespaceSelector/NamespaceSelector.reducer";
import { selectAllNodes, selectAllWorkflows, selectRunningNodes, selectRunningWorkflows, selectStoppedNodes, selectStoppedWorkflows } from "./Dashboard.reducer";
import NodeListItem from "./NodeListItem";

export function Dashboard() {
  const dispatch = useDispatch();
  const namespace = useSelector(selectNamespace);
  const namespaceDisabled = useSelector(selectNamespaceDisabled);
  const allNodes = useSelector(selectAllNodes);
  const runningNodes = useSelector(selectRunningNodes);
  const stoppedNodes = useSelector(selectStoppedNodes);
  const allWorkflows = useSelector(selectAllWorkflows);
  const runningWorkflows = useSelector(selectRunningWorkflows);
  const stoppedWorkflows = useSelector(selectStoppedWorkflows);
  const datesOfWeek = Array.from(Array(7).keys()).map((key) => { const date = new Date(); date.setDate(new Date().getDate() - key); return date.toLocaleDateString('de', { month: 'numeric', day: 'numeric' }) });
  const dates = datesOfWeek.slice(0, 7).reverse();
  useEffect(() => {
    document.title = "Dashboard"
  }, []);
  useEffect(() => {
    if (!namespaceDisabled) {
      dispatch(fetchNodeMetrics(namespace));
      dispatch(fetchWorkflowMetrics(namespace));
    }
  }, [namespace, dispatch, namespaceDisabled]);

  const numberOfWorkflowsLastWeek = datesOfWeek.map((date) => {
    const count = Object.entries(allWorkflows).map((entries) => {
      return new Date(entries[0]).toLocaleDateString('de', { month: 'numeric', day: 'numeric' }) === date ? entries[1].length : 0;
    });
    return count.filter((value) => value > 0)[0] || 0;
  }).reverse();

  const numberOfRunningWorkflowsLastWeek = datesOfWeek.map((date) => {
    const count = Object.entries(runningWorkflows).map((entries) => {
      return new Date(entries[0]).toLocaleDateString('de', { month: 'numeric', day: 'numeric' }) === date ? entries[1].length : 0;
    });
    return count.filter((value) => value > 0)[0] || 0;
  }).reverse();

  const numberOfStoppedWorkflowsLastWeek = datesOfWeek.map((date) => {
    const count = Object.entries(stoppedWorkflows).map((entries) => {
      return new Date(entries[0]).toLocaleDateString('de', { month: 'numeric', day: 'numeric' }) === date ? entries[1].length : 0;
    });
    return count.filter((value) => value > 0)[0] || 0;
  }).reverse();

  const data2 = {
    labels: dates,
    datasets: [
      {
        label: '# of Workflows',
        data: numberOfWorkflowsLastWeek,
        fill: false,
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgba(255, 99, 132, 0.2)',
      },
    ],
  };

  const data3 = {
    labels: dates,
    datasets: [
      {
        label: '# of Failed Workflows',
        data: numberOfRunningWorkflowsLastWeek,
        fill: false,
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgba(255, 99, 132, 0.2)',
      },
    ],
  };

  // console.log(Array.from(Array(7).keys()));

  const data4 = {
    labels: dates,
    datasets: [
      {
        label: '# of Timeouts',
        data: numberOfStoppedWorkflowsLastWeek,
        fill: false,
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgba(255, 99, 132, 0.2)',
      },
    ],
  };

  if (namespaceDisabled) {
    return <h1>Namespace disabled</h1>;
  }

  return (<div>
    <Grid container direction="row">
      <Grid item md={1} />
      <Grid item md={10}>

        <h2>Cluster Status</h2>
        <Divider />
        <br />
        <Grid container spacing={5} direction="row" justifyContent="flex-start" alignContent="stretch">
          <Grid item md={4}>
            <p></p>
            <Grid container>
              <Grid item md={4}>
                <NumberIndicator label="All Nodes" value={allNodes.length} backgroundColor="#999999" />
              </Grid>
              <Grid item md={4}>
                <NumberIndicator label="Running Nodes" value={(runningNodes || []).length} backgroundColor="#00aa00" />
              </Grid>
              <Grid item md={4}>
                <NumberIndicator label="Stopped Nodes" value={(stoppedNodes || []).length} backgroundColor="#aa0000" />
              </Grid>
            </Grid>
          </Grid>
          <Grid item md={8}>
            <Typography>
              <b>All Nodes</b>
            </Typography>
            <Paper style={{ maxHeight: 200, width: '100%', minWidth: 400, overflow: 'auto' }}>
              <List>
                {runningNodes.map(node => <NodeListItem node={node} status="Running" key={`started_nli${node}`}/>)}
                {stoppedNodes.map(node => <NodeListItem node={node} status="Stopped" key={`stopped_nli${node}`}/>)}
              </List>
            </Paper>
          </Grid>
        </Grid>

        <h2>Workflow Status</h2>
        <Divider />
        <br />
        <Grid container spacing={5} direction="row" justifyContent="space-between">
          <Grid item md={4}>
            <PlotChart data={data2} label="All" />
          </Grid>
          <Grid item md={4}>
            <PlotChart data={data3} label="Failed" />
          </Grid>
          <Grid item md={4}>
            <PlotChart data={data4} label="Timeouts" />
          </Grid>
        </Grid>


      </Grid>
      <Grid item md={1} />
    </Grid>
  </div>);
}

export default Dashboard;