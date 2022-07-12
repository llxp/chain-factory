import { Action, createSlice, PayloadAction, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { RootState } from "../../store";
import { useDispatch } from "react-redux";
import { signIn } from "../../api";
import { SignInRequest } from "../../models";

interface LoginState {
  token: string;
  loggedIn: boolean;
}

const initialState: LoginState = {
  token: '',
  loggedIn: false
};

export const signInSlice = createSlice({
  name: "login",
  initialState,
  reducers: {
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
    },
    setLoggedIn: (state, action: PayloadAction<boolean>) => {
      state.loggedIn = action.payload;
    },
    logout: (state, action: PayloadAction<string>) => {
      state.token = '';
      state.loggedIn = false;
    }
  },
});

export const { setLoggedIn } = signInSlice.actions;

const setToken = signInSlice.actions.setToken;

export function signInAsync (username: string, password: string, scopes: string[]): ThunkAction<Promise<boolean>, RootState, undefined, any> {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    try {
      const signInRequest: SignInRequest = {
        username,
        password,
        scopes,
      };
      const response = await signIn(signInRequest);
      if (response.access_token) {
        dispatch(setToken(response.access_token.token));
        dispatch(setLoggedIn(true));
        return true;
      }
      return false;
    } catch (error) {
      console.log(error);
    }
    return false;
  };
  // return apiService.post<string>('/api/login/login', {username, password}).then(
  //   (data: string) => {
  //     dispatch(setToken(data));
  //     dispatch(setLoggedIn(true));
  //     return true;
  //   },
  //   () => {
  //     dispatch(setLoggedIn(false));
  //     return false;
  //   }
  // );
}

export const signOutAsync = (): ThunkAction<Promise<boolean>, RootState, undefined, any> => {
  return (dispatch) => {
    dispatch(setToken(''));
    dispatch(setLoggedIn(false));
    dispatch({
      type: 'signin/logout'
    })
    return new Promise<boolean>(() => true);
  }
}

export const selectToken = (state: RootState) => state.signin.token;
export const selectLoggedIn = (state: RootState) => state.signin.loggedIn;

export type ReduxDispatch = ThunkDispatch<RootState, any, Action>;
export function useReduxDispatch(): ReduxDispatch {
  return useDispatch<ReduxDispatch>();
}

export const SignInSlice = signInSlice.reducer;