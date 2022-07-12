import React from "react";
import ResponsiveAppBar from "./toolbar";

export default function Header() {
  return (
    <header style={{ height: 60 }}>
      <ResponsiveAppBar/>
    </header>
  );
}