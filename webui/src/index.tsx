import React, { lazy, Suspense } from "react";
import ReactDOM from "react-dom";
import "./index.css";
import * as serviceWorker from "./serviceWorker";

import Core from "./pages/core";

const MaterialUIComponent = lazy(
  () => {
    return import('./pages/core/MaterialUI')
      .then(({ MaterialUIComponent }) => ({ default: MaterialUIComponent }));
  });

ReactDOM.render(
  <React.StrictMode>
    <Suspense fallback={<div>Loading... </div>}>
      <MaterialUIComponent>
          <Core/>
      </MaterialUIComponent>
    </Suspense>
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
