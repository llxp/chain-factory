import { Action, ThunkDispatch } from "@reduxjs/toolkit";
import { useDispatch } from "react-redux";
import { RootState } from "../store";

export type ReduxDispatch = ThunkDispatch<RootState, any, Action>;
export default function useReduxDispatch(): ReduxDispatch {
  return useDispatch<ReduxDispatch>();
}