import React from "react";
import { QueryClient, QueryClientProvider } from "react-query";

export const queryClient = new QueryClient();

export interface IQueryWrapperProps {}

export default function QueryWrapper(props: React.PropsWithChildren<IQueryWrapperProps>) {
  return <QueryClientProvider client={queryClient}>{props.children}</QueryClientProvider>;
}