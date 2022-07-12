import { configureStore, ThunkAction, Action, combineReducers } from "@reduxjs/toolkit";
import { NamespaceSlice } from "./pages/core/toolbar/NamespaceSelector/NamespaceSelector.reducer";
import { ToolbarSlice } from "./pages/core/toolbar/Toolbar.reducer";
import { DashboardSlice } from "./pages/dashboard/Dashboard.reducer";
import { TasksSlice } from "./pages/new/TaskTable/TaskTable.reducer";
import { SignInSlice } from "./pages/signin/signin.slice";
import { WorkflowsSlice } from "./pages/workflows/WorkflowTable/WorkflowTable.reducer";

const loadState = () => {
  try {
    const serializedState = localStorage.getItem('state');
    if(serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState);
  } catch (e) {
    return undefined;
  }
};

const peristedState = loadState();

const combinedReducer = combineReducers({
  signin: SignInSlice,
  namespace: NamespaceSlice,
  workflows: WorkflowsSlice,
  tasks: TasksSlice,
  toolbar: ToolbarSlice,
  dashboard: DashboardSlice
});

const rootReducer = (state, action) => {
  if (action.type === 'signin/logout') {
    localStorage.removeItem('state');
    return combinedReducer(undefined, action);
  }
  return combinedReducer(state, action);
};

export const store = configureStore({
  preloadedState: peristedState,
  reducer: rootReducer
});

const saveState = (state) => {
  try {
    const serializedState = JSON.stringify(state);
    localStorage.setItem('state', serializedState);
  } catch (e) {
    // Ignore write errors;
  }
};

store.subscribe(() => {
  saveState(store.getState());
});

export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
