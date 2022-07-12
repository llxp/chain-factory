import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../../../store";
import { Namespace } from "./models";

// State definition
interface NamespaceState {
  namespace: string;
  namespaces: string[];
  namespacesFetching: boolean;
  namespacesError: boolean;
}

// Initial state
const initialState: NamespaceState = {
  namespace: "default",
  namespaces: [],
  namespacesFetching: false,
  namespacesError: false
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
    setFetchNamespaces: (state, action: PayloadAction<boolean>) => {
      state.namespacesFetching = action.payload;
    },
    setNamespacesError: (state, action: PayloadAction<boolean>) => {
      state.namespacesError = action.payload;
    }
  },
});

// export reducers
export const { setNamespace } = namespaceSlice.actions;
export const { setNamespaces } = namespaceSlice.actions;

export const selectNamespace = (state: RootState) => state.namespace.namespace;
export const selectNamespaces = (state: RootState) => state.namespace.namespaces;
export const selectNamespacesFetching = (state: RootState) => state.namespace.namespacesFetching;
export const selectNamespacesError = (state: RootState) => state.namespace.namespacesError;

export const NamespaceSlice = namespaceSlice.reducer;
