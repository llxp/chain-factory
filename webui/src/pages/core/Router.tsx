import React from "react";
import { Route, Routes, Navigate } from "react-router";
import Dashboard from "../dashboard";
import New from "../new";
import Workflows from "../workflows";
import SignIn from "../signin";

export default function Router_Component() {
  return (
      <Routes>
        <Route
          path="/"
          element={<Navigate to="/orchestrator" replace />}
        />
        <Route path="/orchestrator" element={<Navigate to="/orchestrator/dashboard" replace />}/>
        <Route path="/orchestrator/dashboard" element={<Dashboard />} />
        <Route path="/orchestrator/new" element={<New />} />
        <Route path="/orchestrator/workflows" element={<Workflows />} />
        <Route path="/signin" element={<SignIn />} />
      </Routes>
  )
}