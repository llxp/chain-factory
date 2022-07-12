import { makeStyles, Paper, Theme } from "@material-ui/core";
import React from "react";
import BaseCollapsedTable, { IBaseCollapsedTableProps } from "./BaseCollapsedTable";
import CollapsedTablePagination from "./CollapsedTablePagination";
import Spinner from "./Spinner";
import TableToolbar from "./TableToolbar";
import Error from "./Error";

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    width: "100%",
  },
  paper: {
    width: '100%',
    marginBottom: theme.spacing(2),
  }
}));

export interface ICollapsedTableProps extends IBaseCollapsedTableProps {
  showLoadingSpinner?: boolean;
  title?: string;
  count?: number;
  onRefresh?: () => void;
  onSearch?: (text: string) => void;
  onPageChange?: (page: number) => void;
  page: number;
  onRowsPerPageChange?: (rowsPerPage: number) => void;
  rowsPerPage: number;
  searchValue?: string;
  selectedRowsComponent?: JSX.Element;
  errorMessage?: string;
}

export default function CollapsedTable(props: ICollapsedTableProps) {
  const { title, count, page, rowsPerPage, onPageChange, onRowsPerPageChange, onSearch, onRefresh, selectedRows, selectedRowsComponent, showLoadingSpinner, searchValue, errorMessage } = props;
  const pages = Math.ceil((count || 0) / rowsPerPage);
  const classes = useStyles();
  return (<div className={classes.root}>
    <Paper className={classes.paper}>
      <TableToolbar
        title={title}
        searchValue={searchValue || ""}
        onSearch={onSearch}
        onRefresh={onRefresh}
        selectedRows={selectedRows}
        selectedRowsComponent={selectedRowsComponent}
      />
      {showLoadingSpinner
        ? <Spinner />
        : Boolean(errorMessage)
          ? <Error error={errorMessage || ""} />
          : <BaseCollapsedTable {...props as IBaseCollapsedTableProps} />
      }
      <CollapsedTablePagination
        count={count || 0}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        pages={pages}
      />
    </Paper>
  </div>);
}