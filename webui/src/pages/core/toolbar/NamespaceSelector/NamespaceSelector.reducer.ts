import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../../../store";
import { Namespace } from "./models";

// State definition
interface NamespaceState {
  namespace: string;
  namespaces: string[];
  disabledNamespaces: string[];
  namespacesFetching: boolean;
  namespacesError: boolean;
  namespaceEditorOpen: boolean;
  namespaceAddDialogOpen: boolean;
  displayNamespaceKey: boolean;
  rotateNamespaceKeyLoading: boolean;
  namespaceKey: string;
  namespaceDisabled: boolean;
  disableNamespacePromptOpen: boolean;
  deleteNamespacePromptOpen: boolean;
  namspaceCreateError: string;
  namespaceDeleteError: string;
  namespaceDisableError: string;
  namespaceEnableError: string;
  namespaceShowCreateError: boolean;
  namespaceShowDeleteError: boolean;
  namespaceShowDisableError: boolean;
  namespaceShowEnableError: boolean;
}

// Initial state
const initialState: NamespaceState = {
  namespace: "default",
  namespaces: [],
  disabledNamespaces: [],
  namespacesFetching: false,
  namespacesError: false,
  namespaceEditorOpen: false,
  namespaceAddDialogOpen: false,
  displayNamespaceKey: false,
  rotateNamespaceKeyLoading: false,
  namespaceKey: "",
  namespaceDisabled: false,
  disableNamespacePromptOpen: false,
  deleteNamespacePromptOpen: false,
  namspaceCreateError: "",
  namespaceDeleteError: "", 
  namespaceDisableError: "",
  namespaceEnableError: "",
  namespaceShowCreateError: false,
  namespaceShowDeleteError: false,
  namespaceShowDisableError: false,
  namespaceShowEnableError: false,
};

// Slice Definition
export const namespaceSlice = createSlice({
  name: "namespace",
  initialState,
  reducers: {
    setNamespace: (state, action: PayloadAction<string>) => {
      state.namespace = action.payload;
    },
    setNamespaces: (state, action: PayloadAction<Namespace[]>) => {
      state.namespaces = action.payload?.map(n => n.namespace);
    },
    setDisabledNamespaces: (state, action: PayloadAction<Namespace[]>) => {
      state.disabledNamespaces = action.payload?.map(n => n.namespace);
    },
    setNamespacesFetching: (state, action: PayloadAction<boolean>) => {
      state.namespacesFetching = action.payload;
    },
    setNamespacesError: (state, action: PayloadAction<boolean>) => {
      state.namespacesError = action.payload;
    },
    setNamespaceEditorOpen: (state, action: PayloadAction<boolean>) => {
      state.namespaceEditorOpen = action.payload;
    },
    setNamespaceAddDialogOpen: (state, action: PayloadAction<boolean>) => {
      state.namespaceAddDialogOpen = action.payload;
    },
    setDisplayNamespaceKey: (state, action: PayloadAction<boolean>) => {
      state.displayNamespaceKey = action.payload;
    },
    setRotateNamespaceKeyLoading: (state, action: PayloadAction<boolean>) => {
      state.rotateNamespaceKeyLoading = action.payload;
    },
    setNamespaceKey: (state, action: PayloadAction<string>) => {
      state.namespaceKey = action.payload;
    },
    setNamespaceDisabled: (state, action: PayloadAction<boolean>) => {
      state.namespaceDisabled = action.payload;
    },
    setDisableNamespacePromptOpen: (state, action: PayloadAction<boolean>) => {
      state.disableNamespacePromptOpen = action.payload;
    },
    setDeleteNamespacePromptOpen: (state, action: PayloadAction<boolean>) => {
      state.deleteNamespacePromptOpen = action.payload;
    },
    setNamespaceCreateError: (state, action: PayloadAction<string>) => {
      state.namspaceCreateError = action.payload;
    },
    setNamespaceDeleteError: (state, action: PayloadAction<string>) => {
      state.namespaceDeleteError = action.payload;
    },
    setNamespaceDisableError: (state, action: PayloadAction<string>) => {
      state.namespaceDisableError = action.payload;
    },
    setNamespaceEnableError: (state, action: PayloadAction<string>) => {
      state.namespaceEnableError = action.payload;
    },
    setNamespaceShowCreateError: (state, action: PayloadAction<boolean>) => {
      state.namespaceShowCreateError = action.payload;
    },
    setNamespaceShowDeleteError: (state, action: PayloadAction<boolean>) => {
      state.namespaceShowDeleteError = action.payload;
    },
    setNamespaceShowDisableError: (state, action: PayloadAction<boolean>) => {
      state.namespaceShowDisableError = action.payload;
    },
    setNamespaceShowEnableError: (state, action: PayloadAction<boolean>) => {
      state.namespaceShowEnableError = action.payload;
    }
  },
});

// export reducers
export const { setNamespace } = namespaceSlice.actions;
export const { setNamespaces } = namespaceSlice.actions;
export const { setDisabledNamespaces } = namespaceSlice.actions;
export const { setNamespacesFetching } = namespaceSlice.actions;
export const { setNamespaceEditorOpen } = namespaceSlice.actions;
export const { setNamespaceAddDialogOpen } = namespaceSlice.actions;
export const { setDisplayNamespaceKey } = namespaceSlice.actions;
export const { setRotateNamespaceKeyLoading } = namespaceSlice.actions;
export const { setNamespaceKey } = namespaceSlice.actions;
export const { setNamespaceDisabled } = namespaceSlice.actions;
export const { setDisableNamespacePromptOpen } = namespaceSlice.actions;
export const { setDeleteNamespacePromptOpen } = namespaceSlice.actions;
export const { setNamespaceCreateError } = namespaceSlice.actions;
export const { setNamespaceDeleteError } = namespaceSlice.actions;
export const { setNamespaceDisableError } = namespaceSlice.actions;
export const { setNamespaceEnableError } = namespaceSlice.actions;
export const { setNamespaceShowCreateError } = namespaceSlice.actions;
export const { setNamespaceShowDeleteError } = namespaceSlice.actions;
export const { setNamespaceShowDisableError } = namespaceSlice.actions;
export const { setNamespaceShowEnableError } = namespaceSlice.actions;

export const selectNamespace = (state: RootState) => state.namespace.namespace;
export const selectNamespaces = (state: RootState) => state.namespace.namespaces;
export const selectDisabledNamespaces = (state: RootState) => state.namespace.disabledNamespaces;
export const selectNamespacesFetching = (state: RootState) => state.namespace.namespacesFetching;
export const selectNamespacesError = (state: RootState) => state.namespace.namespacesError;
export const selectNamespaceEditorOpen = (state: RootState) => state.namespace.namespaceEditorOpen;
export const selectNamespaceAddDialogOpen = (state: RootState) => state.namespace.namespaceAddDialogOpen;
export const selectDisplayNamespaceKey = (state: RootState) => state.namespace.displayNamespaceKey;
export const selectRotateNamespaceKeyLoading = (state: RootState) => state.namespace.rotateNamespaceKeyLoading;
export const selectNamespaceKey = (state: RootState) => state.namespace.namespaceKey;
export const selectNamespaceDisabled = (state: RootState) => state.namespace.namespaceDisabled;
export const selectDisableNamespacePromptOpen = (state: RootState) => state.namespace.disableNamespacePromptOpen;
export const selectDeleteNamespacePromptOpen = (state: RootState) => state.namespace.deleteNamespacePromptOpen;
export const selectNamespaceCreateError = (state: RootState) => state.namespace.namspaceCreateError;
export const selectNamespaceDeleteError = (state: RootState) => state.namespace.namespaceDeleteError;
export const selectNamespaceDisableError = (state: RootState) => state.namespace.namespaceDisableError;
export const selectNamespaceEnableError = (state: RootState) => state.namespace.namespaceEnableError;
export const selectNamespaceShowCreateError = (state: RootState) => state.namespace.namespaceShowCreateError;
export const selectNamespaceShowDeleteError = (state: RootState) => state.namespace.namespaceShowDeleteError;
export const selectNamespaceShowDisableError = (state: RootState) => state.namespace.namespaceShowDisableError;
export const selectNamespaceShowEnableError = (state: RootState) => state.namespace.namespaceShowEnableError;

export const NamespaceSlice = namespaceSlice.reducer;
