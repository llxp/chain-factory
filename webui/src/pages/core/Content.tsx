import React from "react";
import Header from "./Header";
import Router from "./Router";

export default function Content() {
  return (
    <div className="Page-Container">
      <Header/>
      <div className="Content-Container">
        <Router/>
      </div>
    </div>
  );
}
