import { Grid, Hidden } from '@material-ui/core';
import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { selectNamespaceDisabled } from '../core/toolbar/NamespaceSelector/NamespaceSelector.reducer';
import TaskTable from './TaskTable';

export function New() {
  const namespaceDisabled = useSelector(selectNamespaceDisabled);
  useEffect(() => {
    document.title = "New"
  }, []);

  if (namespaceDisabled) {
    return <h1>Namespace disabled</h1>;
  }
  
  return (
    <div>
      <Hidden xsDown>
      <Grid container spacing={0} justifyContent="center" alignItems="center" wrap="nowrap">
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
