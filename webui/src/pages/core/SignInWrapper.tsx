import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
// import { store } from "../../store";
import { refreshAccessTokenAsync, selectLoggedIn, selectRefreshToken, selectTokenLastUpdated } from "../signin/signin.slice";
import { SignIn } from "../signin";
// import { Header } from "./Header";

// function SignInCheckComponent(history, location) {
//   const loggedIn = store.getState().signin.loggedIn;
//   if (!loggedIn && location.pathname !== '/signin') {
//     history.push('/signin');
//   }
// }

export default function SignInWrapper({ children }) {
  const loggedIn = useSelector(selectLoggedIn);

  const dispatch = useDispatch();
  const refreshToken = useSelector(selectRefreshToken);
  const tokenLastUpdated = useSelector(selectTokenLastUpdated);
  useEffect(() => {
    const time = 1000 * 60 * 10; // refresh token every 10 minutes
    if (loggedIn) {
      if ((tokenLastUpdated + time) < Date.now()) {
        dispatch(refreshAccessTokenAsync(refreshToken));
      }
    }
    const interval = setInterval(() => {
      if (loggedIn) {
        console.log("refreshing token");
        dispatch(refreshAccessTokenAsync(refreshToken));
      }
    }, time);
    return () => {
      clearInterval(interval);
    };
  }, [loggedIn, dispatch, refreshToken]);

  if (!loggedIn) {
    return <SignIn />
  }
  return <>{children}</>;
}