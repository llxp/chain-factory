import { Divider } from "@material-ui/core";
import React from "react";
import { CustomMenuButton } from "./CustomMenuButton";

export interface LargeMenuItemProps {
  text: string;
  path: string;
}

export const LargeMenuItem = (props: LargeMenuItemProps) => {
  return (
    <>
      <Divider orientation="vertical" variant="fullWidth" flexItem key={props.path + 'd1'}/>
      <CustomMenuButton to={props.path} variant="text" key={props.path + 'cmb'}>
        {props.text}
      </CustomMenuButton>
      <Divider orientation="vertical" variant="fullWidth" flexItem key={props.path + 'd2'}/>
    </>
  );
}