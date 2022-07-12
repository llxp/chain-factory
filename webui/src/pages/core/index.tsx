import React from "react";

import "./Core.css";
import ReduxProviderWrapper from '../../components/ReduxProviderWrapper';
import RouterWrapper from "../../components/RouterWrapper";
import Content from "./Content";
import QueryWrapper from "./Query";
import SignInWrapper from "./SignInWrapper";
import SnackbarProviderWrapper from "./Snackbar";

export default function Core() {
  // console.log("Core");
  return (
    <ReduxProviderWrapper>
      <RouterWrapper>
        <QueryWrapper>
          <SnackbarProviderWrapper>
            <SignInWrapper>
              <Content />
            </SignInWrapper>
          </SnackbarProviderWrapper>
        </QueryWrapper>
      </RouterWrapper>
    </ReduxProviderWrapper>
  );
}
