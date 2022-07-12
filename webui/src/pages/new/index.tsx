import { Grid, Hidden } from '@material-ui/core';
import React, { useEffect } from 'react';
import TaskTable from './TaskTable';

export function New() {
  useEffect(() => {
    document.title = "New"
  }, []);
  
  return (
    <div>
      <Hidden xsDown>
      <Grid container spacing={0} justifyContent="center" alignItems="center" wrap="nowrap" style={{marginTop: 50}}>
        <Grid item md={1}/>
        <Grid item md={10}>
          <TaskTable/>
        </Grid>
        <Grid item md={1}/>
      </Grid>
      </Hidden>
      <Hidden smUp><TaskTable/></Hidden>
    </div>
  );
}

export default New;
