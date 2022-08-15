import { Action, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { RootState } from '../../../../store';
import { setDisplayNamespaceKey, setNamespaces, setNamespaceKey, setRotateNamespaceKeyLoading, setDisabledNamespaces, setNamespacesFetching, setNamespaceDisabled, setNamespace } from "./NamespaceSelector.reducer";
import { deleteNamespace, disabledNamespaces, disableNamespace, enableNamespace, namespaces, rotateNamespacePassword } from "../../../../api";

export function fetchNamespaces(): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    dispatch(setNamespacesFetching(true));
    const namespacesResult = await namespaces();
    const disabledNamespacesResult = await disabledNamespaces();
    dispatch(setNamespaces(namespacesResult));
    dispatch(setDisabledNamespaces(disabledNamespacesResult));
    dispatch(setNamespacesFetching(false));
  };
}

export function rotateNamespaceKey(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    dispatch(setDisplayNamespaceKey(false));
    dispatch(setRotateNamespaceKeyLoading(true));
    const namespaceKeyResponse = await rotateNamespacePassword(namespace);
    dispatch(setRotateNamespaceKeyLoading(false));
    if (namespaceKeyResponse && namespaceKeyResponse.length > 0) {
      dispatch(setDisplayNamespaceKey(true));
      dispatch(setNamespaceKey(namespaceKeyResponse));
    }
  }
}

export function disableNamespaceAsync(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    await disableNamespace(namespace);
    dispatch(fetchNamespaces());
    dispatch(setNamespaceDisabled(true));
  }
}

export function enableNamespaceAsync(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    await enableNamespace(namespace);
    dispatch(fetchNamespaces());
    dispatch(setNamespaceDisabled(false));
  }
}

export function deleteNamespaceAsync(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    await deleteNamespace(namespace);
    dispatch(fetchNamespaces());
    dispatch(setNamespace("default"));
  }
}