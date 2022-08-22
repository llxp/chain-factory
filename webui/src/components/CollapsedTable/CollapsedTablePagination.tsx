import { Grid, IconButton, makeStyles, TablePagination, Theme } from "@material-ui/core";
import React from "react";
import SkipPreviousIcon from '@material-ui/icons/SkipPrevious';
import SkipNextIcon from '@material-ui/icons/SkipNext';
import { Pagination } from "@material-ui/lab";

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    //height: "52px",
  },
  pagination: {
    backgroundColor: theme.palette.background.paper,
  }
}));

export interface ICollapsedTablePaginationProps {
  count: number;
  rowsPerPage: number;
  page: number;
  onPageChange?: (page: number) => void;
  onRowsPerPageChange?: (rowsPerPage: number) => void;
}

export default function CollapsedTablePagination(props: ICollapsedTablePaginationProps) {
  const { count, rowsPerPage, page, onPageChange, onRowsPerPageChange } = props;
  const classes = useStyles();

  const handleChangePage = (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent> | null,
    page: number
  ) => {
    onPageChange?.(page);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onRowsPerPageChange?.(+event.target.value);
    onPageChange?.(0);
  };

  return <Grid container direction="row" justifyContent="center" alignItems="center" alignContent="center" className={classes.root}>
      <Grid item md={5}></Grid>
      <Grid item md={3}>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={count}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          className={classes.pagination}
          ActionsComponent={({ count, page, rowsPerPage, onPageChange }) => <div></div>}
        />
      </Grid>
      <Grid item>
        <Pagination
        count={Math.ceil(count / rowsPerPage)} page={page + 1}
        onChange={(event: any, page: number) => onPageChange?.(page - 1)}
        boundaryCount={1}
        siblingCount={0}
        showFirstButton
        showLastButton
      />
      </Grid>
    </Grid>;
}