import { ThunkAction } from "@reduxjs/toolkit";
import { RootState } from '../../../../store';
import { setNamespaces } from "./NamespaceSelector.reducer";
import { namespaces } from "../../../../api";

export function fetchNamespaces(): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch, getState) => {
    const namespacesResult = await namespaces();
    dispatch(setNamespaces(namespacesResult));
  };
}