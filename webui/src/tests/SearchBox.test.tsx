/**
 * @jest-environment jsdom
 */

import React from 'react';
import {render, fireEvent, cleanup} from '@testing-library/react';
import SearchBox from '../components/CollapsedTable/SearchBox';

afterEach(cleanup)


it('button click changes props', () => {
  const { getByText } = render(<SearchBox/>)

  console.log(getByText("<span>Search</span>"));

  expect(getByText(/Moe/i).textContent).toBe("Moe")

  fireEvent.click(getByText("Change Name"))

  expect(getByText(/Steve/i).textContent).toBe("Steve")
})