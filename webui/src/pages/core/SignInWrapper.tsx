import React from "react";
import { useSelector } from "react-redux";
// import { store } from "../../store";
import { selectLoggedIn } from "../signin/signin.slice";
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
  if (!loggedIn) {
    return <SignIn />
  }
  return <>{children}</>;
}