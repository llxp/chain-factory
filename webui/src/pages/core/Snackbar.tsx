import { SnackbarProvider } from "notistack";
import React from "react";

export default function SnackbarProviderWrapper({ children }) {
  return <SnackbarProvider maxSnack={1000}>{children}</SnackbarProvider>;
}