import { useSnackbar } from "notistack";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import useReduxDispatch from "../../../utils/ReduxDispatch";
import { selectNamespace } from "../../core/toolbar/NamespaceSelector/NamespaceSelector.reducer";
import CollapsedTable from "../../../components/CollapsedTable";
import { ICollapsedTableRowProps } from "../../../components/CollapsedTable/CollapsedTableRow";
import TaskSubTable from "./TaskSubTable";
import { fetchAvailableTasks, startTask, updateAvailableTasks } from "./TaskTable.service";
import { clearRegisteredTasks, selectRegisteredTasks, selectRegisteredTasksError, selectRegisteredTasksFetching, selectTaskDetailsOpened, selectTasksPage, selectTasksPerPage, selectTasksSearch, setTaskDetailsOpened, setTasksPage, setTasksPerPage, setTasksSearch } from "./TaskTable.reducer";
import { useEffect } from "react";

export default function TaskTable() {
  const reduxDispatch = useReduxDispatch();
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const namespace = useSelector(selectNamespace);
  const registeredTasks = useSelector(selectRegisteredTasks);
  const registeredTasksFetching = useSelector(selectRegisteredTasksFetching);
  const registeredTasksError = useSelector(selectRegisteredTasksError);
  const tasksPage = useSelector(selectTasksPage);
  const tasksPerPage = useSelector(selectTasksPerPage);
  const taskDetailsOpened = useSelector(selectTaskDetailsOpened);
  const tasksSearch = useSelector(selectTasksSearch);

  const handleRowsPerPageChange = (rowsPerPage: number) => dispatch(setTasksPerPage(rowsPerPage));
  const handleRefresh = () => dispatch(fetchAvailableTasks(namespace, tasksPage, tasksPerPage, tasksSearch));

  useEffect(() => {
    dispatch(clearRegisteredTasks());
    dispatch(fetchAvailableTasks(namespace, tasksPage, tasksPerPage, tasksSearch));
  }, [namespace, tasksPage, tasksPerPage, tasksSearch, dispatch]);

  useEffect(() => {
    const interval = setInterval(() => {
      dispatch(updateAvailableTasks(namespace, tasksPage, tasksPerPage, tasksSearch));
    }, 5000);
    return () => clearInterval(interval);
  });

  const handleSearch = (text: string) => {
    dispatch(setTasksSearch(text));
    dispatch(setTasksPage(0));
  }

  const handleStart = (
    task: string,
    selectedArguments: Map<string, string>,
    nodeSelection: string,
    tags: string[],
    namespace: string
  ) => {
    reduxDispatch(
      startTask(namespace, nodeSelection, task, selectedArguments, tags)
    ).then(
      () => {
        enqueueSnackbar("Task started!", {
          variant: "success",
          autoHideDuration: 3000,
        });
      },
      () => {
        enqueueSnackbar("Error starting task!", {
          variant: "error",
          autoHideDuration: 3000,
        });
      }
    );
  };

  const rows: ICollapsedTableRowProps[] = (registeredTasks?.items || []).map((task) => {
    return {
      firstKey: "name",
      row: task,
      rowComponent: (
        <TaskSubTable
          arguments={task.arguments}
          nodeNames={task.nodeNames}
          handleStart={handleStart}
          task={task.task.name}
          namespace={task.namespace}
          key={task.namespace + task.task.name}
        />
      ),
      key: task.namespace + task.task.name
    };
  });

  return (<CollapsedTable
    expandedRows={taskDetailsOpened}
    setExpandedRows={(expandedRowsTemp) => {
      dispatch(setTaskDetailsOpened(expandedRowsTemp));
    }}
    rows={rows}
    headerLabels={["Name", "Namespace"]}
    rowColumnOrder={['name', 'namespace']}
    onRefresh={handleRefresh}
    onSearch={handleSearch}
    onPageChange={(page: number) => dispatch(setTasksPage(page))}
    onRowsPerPageChange={handleRowsPerPageChange}
    page={tasksPage}
    rowsPerPage={tasksPerPage}
    count={registeredTasks?.totalCount || 0}
    title="Run a new task"
    showLoadingSpinner={registeredTasksFetching}
    searchValue={tasksSearch}
    errorMessage={registeredTasksError || ""}
  />);
}