export class environment {
    constructor() {
        console.log(window.__RUNTIME_CONFIG__);
        this.apiEndpoint = window.__RUNTIME_CONFIG__.API_URL || "default";
    }
  production: boolean = true;
  apiEndpoint: string = '';
  authenticationEnabled: boolean = true;
};
