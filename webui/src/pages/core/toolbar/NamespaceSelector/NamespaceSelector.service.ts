import { Action, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { RootState } from '../../../../store';
import { setDisplayNamespaceKey, setNamespaces, setNamespaceKey, setRotateNamespaceKeyLoading, setDisabledNamespaces, setNamespacesFetching, setNamespaceDisabled, setNamespace, setNamespaceEditorOpen, setNamespaceAddDialogOpen, setNamespaceCreateError, setNamespaceShowCreateError } from "./NamespaceSelector.reducer";
import { createNamespace, deleteNamespace, disabledNamespaces, disableNamespace, enableNamespace, namespaces, rotateNamespacePassword } from "../../../../api";
import { HTTPException, IsHTTPException } from '../../../../models';
import { Namespace } from "./models";

export function fetchNamespaces(): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    dispatch(setNamespacesFetching(true));
    const namespacesResult = await namespaces();
    const disabledNamespacesResult = await disabledNamespaces();
    dispatch(setNamespaces(namespacesResult as Namespace[]));
    dispatch(setDisabledNamespaces(disabledNamespacesResult as Namespace[]));
    dispatch(setNamespacesFetching(false));
  };
}

export function rotateNamespaceKey(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    dispatch(setDisplayNamespaceKey(false));
    dispatch(setRotateNamespaceKeyLoading(true));
    const namespaceKeyResponse = await rotateNamespacePassword(namespace);
    dispatch(setRotateNamespaceKeyLoading(false));
    if (namespaceKeyResponse && (namespaceKeyResponse as string).length > 0) {
      dispatch(setDisplayNamespaceKey(true));
      dispatch(setNamespaceKey(namespaceKeyResponse as string));
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
    dispatch(setNamespaceDisabled(false));
  }
}

export function createNamespaceAsync(namespace: string): ThunkAction<Promise<void>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    if (namespace.length <= 0) {
      dispatch(setNamespaceCreateError("empty"));
      dispatch(setNamespaceShowCreateError(true));
    } else {
      try {
        const createNamespaceResponse = await createNamespace(namespace);
        if (createNamespaceResponse.status === 200) {
          dispatch(fetchNamespaces());
          dispatch(setNamespace(namespace));
          dispatch(setNamespaceDisabled(false));
          dispatch(setNamespaceEditorOpen(true));
          dispatch(setNamespaceAddDialogOpen(false));
          dispatch(setNamespaceShowCreateError(false));
        } else {
          dispatch(setNamespaceCreateError("An unknown error occurred"));
          dispatch(setNamespaceShowCreateError(true));
        }
      } catch (error: any) {
        if (error.response) {
          if (error.response.status === 409) {
            dispatch(setNamespaceCreateError(error.response.data.detail));
            dispatch(setNamespaceShowCreateError(true));
          } else {
            dispatch(setNamespaceCreateError("An unknown error occurred"));
            dispatch(setNamespaceShowCreateError(true));
          }
        } else {
          dispatch(setNamespaceCreateError("An unknown error occurred"));
          dispatch(setNamespaceShowCreateError(true));
        }
      }
    }
  }
}