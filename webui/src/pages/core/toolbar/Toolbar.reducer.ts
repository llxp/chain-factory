import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../../store";

// State definition
interface NamespaceState {
  selectedMenuItem: string;
}

// Initial state
const initialState: NamespaceState = {
  selectedMenuItem: ""
};

// Slice Definition
export const toolbarSlice = createSlice({
  name: "toolbar",
  initialState,
  reducers: {
    setSelectedMenuItem: (state, action: PayloadAction<string>) => {
      state.selectedMenuItem = action.payload;
    },
  },
});

// export reducers
export const { setSelectedMenuItem } = toolbarSlice.actions;

export const selectSelectedMenuItem = (state: RootState) => state.toolbar.selectedMenuItem;

export const ToolbarSlice = toolbarSlice.reducer;
