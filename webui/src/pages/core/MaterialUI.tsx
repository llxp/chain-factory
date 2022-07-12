import React from "react";
import { ThemeProvider } from "@material-ui/core/styles";
import { CssBaseline } from "@material-ui/core";
import theme from "./theme";

interface MaterialUIProps {}
export function MaterialUIComponent(props: React.PropsWithChildren<MaterialUIProps>) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {props.children}
    </ThemeProvider>
  );
}