import React from "react";
import { BrowserRouter } from "react-router-dom";

export default function RouterWrapper({children}) {
  return (
    <BrowserRouter>
    {children}
    </BrowserRouter>
  );
}