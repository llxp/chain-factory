import { Menu, MenuItem } from "@material-ui/core";
import React from "react";
import { useDispatch } from "react-redux";
import { signOutAsync } from "../../../signin/signin.slice";

export default function LogoutMenu({anchorEl, setAnchorEl}) {
  const dispatch = useDispatch();
  const handleClose = () => {
    setAnchorEl(null);
  };
  const handleLogout = () => {
    dispatch(signOutAsync());
    handleClose();
  };
  return (<Menu
    id="simple-menu"
    anchorEl={anchorEl}
    keepMounted
    MenuListProps={{style: { padding: 0}}}
    open={Boolean(anchorEl)}
    onClose={handleClose}
    style={{left: 15, width: 94}}
    transformOrigin={{horizontal: "left", vertical: -64}}
  >
    <MenuItem onClick={handleLogout} style={{marginLeft: 0, height: 64, textAlign: 'center', paddingLeft: 10}}>Logout</MenuItem>
  </Menu>);
}