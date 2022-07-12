import { Grid, IconButton, makeStyles, TablePagination, Theme } from "@material-ui/core";
import React from "react";
import SkipPreviousIcon from '@material-ui/icons/SkipPrevious';
import SkipNextIcon from '@material-ui/icons/SkipNext';

const useStyles = makeStyles((theme: Theme) => ({
  pagination: {
    backgroundColor: theme.palette.background.paper,
  }
}));

export default function CollapsedTablePagination({count, rowsPerPage, page, onPageChange, onRowsPerPageChange, pages}) {
  const classes = useStyles();

  const jumpToFirstPage = () => {
    onPageChange?.(0);
  };

  const jumpToLastPage = () => {
    onPageChange?.(pages - 1);
  };

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

  const disabledFirstPage = (pages <= 0 || page <= 0);
  const disabledLastPage = (pages <= 0 || (page + 1) >= pages);

  return (
    <Grid container direction="row">
      <Grid item md={10}>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50, 100, 250, 500]}
          component="div"
          count={count}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          className={classes.pagination}
        />
      </Grid>
      <Grid item md={2} className={classes.pagination}>
        <IconButton
          size="medium"
          onClick={jumpToFirstPage}
          disabled={disabledFirstPage}
        ><SkipPreviousIcon/></IconButton>
        <IconButton
          size="medium"
          onClick={jumpToLastPage}
          disabled={disabledLastPage}
        ><SkipNextIcon/></IconButton>
      </Grid>
    </Grid>
  );
}