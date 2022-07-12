import React from "react";
import { render } from "@testing-library/react";
import { Provider } from "react-redux";
import { store } from "../store";
import Core from "../pages/core";

test("renders learn react link", () => {
  const { getByText } = render(
    <Provider store={store}>
      <Core />
    </Provider>
  );

  expect(getByText(/learn/i)).toBeInTheDocument();
});
