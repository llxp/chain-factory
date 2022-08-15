import { Dialog, DialogTitle } from "@material-ui/core";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectNamespaceAddDialogOpen, setNamespaceAddDialogOpen } from "./NamespaceSelector.reducer";

export default function NamespaceAddDialog() {
  const namespaceAddDialogOpen = useSelector(selectNamespaceAddDialogOpen);
  const dispatch = useDispatch();
  return <Dialog open={namespaceAddDialogOpen} onClose={()=>dispatch(setNamespaceAddDialogOpen(false))}>
    <DialogTitle>Add New Namespace</DialogTitle>
  </Dialog>;
}