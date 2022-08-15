import { Action, createSlice, PayloadAction, ThunkAction, ThunkDispatch } from "@reduxjs/toolkit";
import { RootState } from "../../store";
import { useDispatch } from "react-redux";
import { getAccessTokenWithRefreshToken, signIn } from "../../api";
import { SignInRequest } from "../../models";

interface LoginState {
  token: string;
  refreshToken: string;
  loggedIn: boolean;
  tokenLastUpdated: number;
}

const initialState: LoginState = {
  token: '',
  refreshToken: '',
  loggedIn: false,
  tokenLastUpdated: 0,
};

export const signInSlice = createSlice({
  name: "login",
  initialState,
  reducers: {
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.tokenLastUpdated = Date.now();
    },
    setRefreshToken: (state, action: PayloadAction<string>) => {
      state.refreshToken = action.payload;
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

const { setToken, setRefreshToken } = signInSlice.actions;

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
        if (response.refresh_token) {
          dispatch(setRefreshToken(response.refresh_token.token));
        }
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
  return (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    dispatch(setToken(''));
    dispatch(setLoggedIn(false));
    dispatch({
      type: 'signin/logout'
    })
    return new Promise<boolean>(() => true);
  }
}

export const refreshAccessTokenAsync = (refreshToken: string): ThunkAction<Promise<boolean>, RootState, undefined, any> => {
  return async (dispatch: ThunkDispatch<RootState, undefined, Action>) => {
    const accessToken = await getAccessTokenWithRefreshToken(refreshToken);
    if (accessToken && accessToken.token && accessToken) {
      dispatch(setToken(accessToken.token));
    }
    return new Promise<boolean>(() => true);
  }
}


export const selectToken = (state: RootState) => state.signin.token;
export const selectLoggedIn = (state: RootState) => state.signin.loggedIn;
export const selectRefreshToken = (state: RootState) => state.signin.refreshToken;
export const selectTokenLastUpdated = (state: RootState) => state.signin.tokenLastUpdated;

export type ReduxDispatch = ThunkDispatch<RootState, any, Action>;
export function useReduxDispatch(): ReduxDispatch {
  return useDispatch<ReduxDispatch>();
}

export const SignInSlice = signInSlice.reducer;