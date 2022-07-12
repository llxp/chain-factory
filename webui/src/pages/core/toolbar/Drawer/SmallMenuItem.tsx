import { ListItem } from "@material-ui/core";
import React from "react";
import { Link } from "react-router-dom";

export function SmallMenuItem({text, path}) {
  return (
    <ListItem key={text} component={Link} to={path} divider button>
      {" "}{text}{" "}
    </ListItem>
  );
}