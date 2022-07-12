export interface SignInRequest {
  username: string;
  password: string;
  scopes: string[];
}

export interface SignInResponse {
  access_token: {
    token: string;
    token_type: string;
  },
  refresh_token: {
    token: string;
    token_type: string;
  }
}