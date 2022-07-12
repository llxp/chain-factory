import { useSnackbar, VariantType } from "notistack";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import useReduxDispatch from "../../../utils/ReduxDispatch";
import { selectNamespace } from "../../core/toolbar/NamespaceSelector/NamespaceSelector.reducer";
import { ListItemType } from "./models";
import CollapsedTable from "../../../components/CollapsedTable";
import { ICollapsedTableRowProps } from "../../../components/CollapsedTable/CollapsedTableRow";
import WorkflowSubTable from "./WorkflowSubTable";
import { fetchWorkflows, fetchWorkflowStatus, handleWorkflow } from "./WorkflowTable.service";
import { clearWorkflows, selectSelectedWorkflows, selectWorkflowDetailsOpened, selectWorkflows, selectWorkflowsError, selectWorkflowsFetching, selectWorkflowsPage, selectWorkflowsPerPage, selectWorkflowsSearch, selectWorkflowsSortBy, selectWorkflowsSortOrder, setSelectedWorkflows, setWorkflowDetailsOpened, setWorkflowsPage, setWorkflowsPerPage, setWorkflowsSearch } from "./WorkflowTable.reducer";
import TableHeadButtonControl from "./TableHeadButtonControl";

export interface IProps { }

export default function WorkflowTable(props: IProps) {
  const reduxDispatch = useReduxDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const namespace = useSelector(selectNamespace);
  const dispatch = useDispatch();

  const workflows = useSelector(selectWorkflows);
  const workflowsFetching = useSelector(selectWorkflowsFetching);
  const workflowsError = useSelector(selectWorkflowsError);
  const expandedRows = useSelector(selectWorkflowDetailsOpened);
  const sortBy = useSelector(selectWorkflowsSortBy);
  const sortOrder = useSelector(selectWorkflowsSortOrder);
  const searchTerm = useSelector(selectWorkflowsSearch);
  const workflowsPage = useSelector(selectWorkflowsPage);
  const workflowsPerPage = useSelector(selectWorkflowsPerPage);
  const selectedWorkflows = useSelector(selectSelectedWorkflows);

  useEffect(() => {
    dispatch(clearWorkflows());
    dispatch(fetchWorkflows(namespace, workflowsPage, workflowsPerPage, searchTerm, sortBy, sortOrder));
  }, [namespace, workflowsPage, workflowsPerPage, searchTerm, sortBy, sortOrder, dispatch]);

  useEffect(() => {
    const interval = setInterval(() => {
      dispatch(fetchWorkflowStatus(namespace, workflows.items.map(workflow => workflow.workflowId)));
    }, 10000);
    return () => clearInterval(interval);
  }, [namespace, workflows, enqueueSnackbar, dispatch]);

  const newSnackbar = (text: string, variant: VariantType) => {
    enqueueSnackbar(text, {
      variant: variant,
      autoHideDuration: 3000,
    });
  };

  const handleAction = (action: string) => (workflow_id: string, namespace: string) => {
    reduxDispatch(handleWorkflow(namespace, workflow_id, action)).then(
      () => { newSnackbar(`Task ${action}!`, "success"); },
      () => { newSnackbar(`Error ${action}ing task!`, "error"); }
    );
  };

  const handleSelectedAction = (action: string) => {
    for (const selectedWorkflow of selectedWorkflows) {
      const workflow = workflows.items.find((workflow) => {
        const key = workflow.namespace + workflow.workflowId + workflow.createdDate + workflow.entryTask;
        return selectedWorkflow === key;
      });
      if (workflow && workflow.status.toUpperCase() === "RUNNING") {
        handleAction(action)(workflow?.workflowId, workflow?.namespace);
      }
    }
  };

  const handleRefresh = () => dispatch(fetchWorkflows(namespace, workflowsPage, workflowsPerPage, searchTerm, sortBy, sortOrder));
  const handlePageChange = (page: number) => dispatch(setWorkflowsPage(page));
  const handleRowsPerPageChange = (rowsPerPage: number) => dispatch(setWorkflowsPerPage(rowsPerPage));

  const handleSearch = (text: string) => {
    dispatch(setWorkflowsSearch(text));
    dispatch(setWorkflowsPage(0));
  };

  const rows: ICollapsedTableRowProps[] = (workflows?.items || []).map((workflow: ListItemType) => {
    return {
      firstKey: "createdDate",
      row: workflow,
      rowComponent: <WorkflowSubTable
        workflowId={workflow.workflowId}
        namespace={workflow.namespace}
        onStop={handleAction('stop')}
        onAbort={handleAction('abort')}
        onRestart={handleAction('restart')}
        key={workflow.key + "234"}
        status={workflow.status}
      />,
      key: workflow.key,
    }
  });

  return (<CollapsedTable
    expandedRows={expandedRows}
    setExpandedRows={(expandedRowsTemp) => { dispatch(setWorkflowDetailsOpened(expandedRowsTemp)); }}
    rows={rows}
    headerLabels={["Timestamp", "Entry Task", "Status", "Tags", "Namespace"]}
    rowColumnOrder={['createdDate', 'entryTask', 'status', 'tags', 'namespace']}
    onRefresh={handleRefresh}
    onSearch={handleSearch}
    onPageChange={handlePageChange}
    onRowsPerPageChange={handleRowsPerPageChange}
    page={workflowsPage}
    rowsPerPage={workflowsPerPage}
    count={workflows.totalCount}
    title="Workflows"
    selectable
    selectedRowsComponent={<TableHeadButtonControl onStop={() => handleSelectedAction('stop')} onAbort={() => handleSelectedAction('abort')} onRestart={() => handleSelectedAction('restart')} />}
    searchValue={searchTerm}
    showLoadingSpinner={workflowsFetching}
    selectedRows={selectedWorkflows}
    setSelectedRows={(selectedWorkflowsTemp) => { dispatch(setSelectedWorkflows(selectedWorkflowsTemp)); }}
    errorMessage={workflowsError}
  />);
}