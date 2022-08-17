import { Button, Dialog, DialogContent, DialogTitle, Divider, FormControl, Grid, IconButton, Input, InputAdornment, InputLabel, Tooltip, Typography } from "@material-ui/core";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectDisplayNamespaceKey, selectNamespace, selectNamespaceDisabled, selectNamespaceEditorOpen, selectNamespaceKey, setDisplayNamespaceKey, setNamespaceEditorOpen, setNamespaceKey } from "./NamespaceSelector.reducer";
import EditIcon from '@material-ui/icons/Edit';
import { deleteNamespaceAsync, disableNamespaceAsync, enableNamespaceAsync, rotateNamespaceKey } from "./NamespaceSelector.service";

export default function NamespaceEditor() {
  const selectedNamespace = useSelector(selectNamespace);
  const namespaceDisabled = useSelector(selectNamespaceDisabled);
  const namespaceEditorOpen = useSelector(selectNamespaceEditorOpen);
  const displayNamespaceKey = useSelector(selectDisplayNamespaceKey);
  const namespaceKey = useSelector(selectNamespaceKey);
  const dispatch = useDispatch();
  const onClose = () => {
    dispatch(setNamespaceEditorOpen(false));
    dispatch(setNamespaceKey(''));
    dispatch(setDisplayNamespaceKey(false));
  }
  const NamespaceKey = () => {
    if (namespaceDisabled) {
      return <></>;
    }
    if (displayNamespaceKey) {
      return <>
        <Typography variant="body2" color="textSecondary">
          Namespace Key
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {namespaceKey}
        </Typography>
      </>;
    }
    return <>
      <Typography variant="body2" color="textSecondary">
        Namespace Key
      </Typography>
      <Typography variant="body2" color="textSecondary">
      <i className="material-icons">lock</i>(will be shown <b>only once</b> after clicking on "Rotate Key")
      </Typography>
    </>;
  };
  const DisableNamespaceButton = () => {
    return <Button variant="contained" color="primary" onClick={()=>{
      onClose();
      if (namespaceDisabled) {
        dispatch(enableNamespaceAsync(selectedNamespace));
      } else {
        dispatch(disableNamespaceAsync(selectedNamespace));
      }
    }}>
      {namespaceDisabled ? "Enable": "Disable"}
    </Button>;
  };
  const RotateNamespaceKeyButton = () => {
    if (namespaceDisabled) {
      return <></>;
    }
    return <Grid item xs={4}><Button variant="contained" style={{
      backgroundColor: "#ffc107",
      color: "#ffffff"
    }} onClick={()=>{
      dispatch(rotateNamespaceKey(selectedNamespace));
    }}>
      Rotate Key
    </Button></Grid>;
  }
  const DeleteNamespaceButton = () => {
    return <Button variant="contained" style={{
      backgroundColor: "#ff0000",
      color: "#ffffff"
    }} onClick={()=>{
      onClose();
      dispatch(deleteNamespaceAsync(selectedNamespace));
    }}>
      Delete
    </Button>
  };
  return <Dialog
  open={namespaceEditorOpen}
  onClose={()=>{
    onClose();
  }}
  fullWidth
  maxWidth="xs"
  >
    <DialogTitle>Manage Namespace <b>{selectedNamespace}</b></DialogTitle>
    <DialogContent>
      <Grid container spacing={3} direction="column">
        <Grid item>
          <Tooltip title="Rename Namespace" arrow>
          <FormControl fullWidth>
            <InputLabel htmlFor="namespace-rename">New namespace name</InputLabel>
            <Input
              id="namespace-rename"
              fullWidth
              type="text"
              endAdornment={<InputAdornment position="end">
                <IconButton color="inherit" aria-label="Rename namespace" onClick={()=>{
                  onClose();
                }}>
                  <EditIcon />
                </IconButton>
              </InputAdornment>} />
          </FormControl>
          </Tooltip>
        </Grid>
        <Grid item>
          <Grid container direction="row">
            <Grid item xs={4}>
              <DeleteNamespaceButton />
            </Grid>
            <Grid item xs={4}>
              <DisableNamespaceButton />
            </Grid>
            <RotateNamespaceKeyButton />
          </Grid>
        </Grid>
        <Grid item>
          <Divider />
        </Grid>
        <Grid item>
          <NamespaceKey />
        </Grid>
      </Grid>
    </DialogContent>
  </Dialog>;
}