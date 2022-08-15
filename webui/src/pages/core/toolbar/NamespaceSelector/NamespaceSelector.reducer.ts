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

export const NamespaceSlice = namespaceSlice.reducer;
