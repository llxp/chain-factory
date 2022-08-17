import { Button, Dialog, DialogContent, DialogTitle, TextField, Typography } from "@material-ui/core";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectNamespaceAddDialogOpen, selectNamespaceCreateError, selectNamespaceShowCreateError, setNamespaceAddDialogOpen, setNamespaceCreateError, setNamespaceShowCreateError } from "./NamespaceSelector.reducer";
import { createNamespaceAsync } from "./NamespaceSelector.service";

export default function NamespaceAddDialog() {
  const [namespaceName, setNamespaceName] = React.useState("");
  const namespaceAddDialogOpen = useSelector(selectNamespaceAddDialogOpen);
  const namespaceShowCreateError = useSelector(selectNamespaceShowCreateError);
  const namspaceCreateError = useSelector(selectNamespaceCreateError);
  const dispatch = useDispatch();
  const onClose = () => {
    dispatch(setNamespaceAddDialogOpen(false));
    dispatch(setNamespaceCreateError(""));
    dispatch(setNamespaceShowCreateError(false));
  };
  const onsubmit = () => {
    dispatch(createNamespaceAsync(namespaceName));
  }

  useEffect(() => {
    dispatch(setNamespaceCreateError(""));
    dispatch(setNamespaceShowCreateError(false));
  }, []);
  
  return <Dialog open={namespaceAddDialogOpen} onClose={()=>onClose()}>
    <DialogTitle>Add New Namespace</DialogTitle>
    <DialogContent>
      <TextField label="Namespace" fullWidth onChange={(event)=>{
        const value = event.target.value;
        setNamespaceName(value);
        if (value.length > 0) {
          dispatch(setNamespaceShowCreateError(value.length <= 0));
          dispatch(setNamespaceCreateError(value.length > 0 ? "empty": ""));
        }
      }} value={namespaceName}/>
      <Button variant="contained" color="primary" style={{marginTop: 10}} onClick={()=>onsubmit()}>
        Add
      </Button>
      <Typography variant="body2" color="textSecondary" style={(namespaceShowCreateError && namspaceCreateError === "empty") ? {color: "#ff0000"} : {}}>
        <i className="material-icons">warning</i>
        Namespace name must be unique and cannot be empty.
      </Typography>
      <Typography variant="body2" color="textSecondary">
        <i className="material-icons">label</i>
        After the creation of the namespace <br/>you first need to rotate the key get the key <br/>(to use it in the worker node)
      </Typography>
      {namespaceShowCreateError && namspaceCreateError !== "empty" && <Typography variant="body2" color="textSecondary" style={(namespaceShowCreateError && namspaceCreateError !== "empty") ? {color: "#ff0000"} : {}}>
        <i className="material-icons">error</i>
        {namspaceCreateError}
      </Typography>}
    </DialogContent>
  </Dialog>;
}