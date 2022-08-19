import React from "react";
import Header from "./Header";
import Router from "./Router";

export default function Content() {
  return (
    <div className="Page-Container">
      <Header/>
      <div className="Content-Container" style={{
        height: "calc(100vh - 110px)",
        marginTop: "50px",
      }}>
        <Router/>
      </div>
    </div>
  );
}
