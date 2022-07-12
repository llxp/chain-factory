import { Button } from "@material-ui/core";
import { darken, makeStyles, Theme } from "@material-ui/core/styles";
import { Link } from "react-router-dom";
import React from "react";
import { useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import { selectLoggedIn } from "../../../signin/signin.slice";

export interface CustomMenuButtonProps {
  children: React.ReactNode;
  to?: string;
  variant?: 'text' | 'outlined' | 'contained';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  ref?: any;
}

const useStyles = (pathname: string, to) => makeStyles((theme: Theme) => ({
  root: {
    paddingLeft: 10,
    paddingRight: 10,
    marginRight: 0,
    paddingTop: 18,
    paddingBottom: 18,
    backgroundColor: pathname === to ? darken(theme.palette.primary.main, 0.1) : theme.palette.primary.main,
  }
}));

export const CustomMenuButton = (props: CustomMenuButtonProps) => {
  const { children, to, variant, onClick, ref } = props;
  const location = useLocation();

  const classes = useStyles(location.pathname, to)();

  const loggedIn = useSelector(selectLoggedIn);
  if (!loggedIn || location.pathname === '/signin') {
    return <></>;
  }

  return <Button
    color="inherit"
    variant={variant}
    className={classes.root}
    component={Link}
    to={to}
    onClick={onClick}
    ref={ref}
  >{children}</Button>;
};