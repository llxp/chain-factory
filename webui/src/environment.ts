import { environment as env_dev } from "./environment.dev";
import { environment as env_prod } from "./environment.prod";

export const prodEnabled =
  !process.env.NODE_ENV || process.env.NODE_ENV === "development";

export const environment = prodEnabled ? new env_dev() : new env_prod();
