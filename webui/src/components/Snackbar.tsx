import { Button } from "@material-ui/core";
import React from "react";

export function snackbarAction(closeSnackbar) {
  return (key) => {
    return <Button onClick={() => {closeSnackbar(key);}}>Dismiss</Button>;
  };
}