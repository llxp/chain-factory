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

export interface RefreshTokenResponse {
  token: string;
  token_type: string;
}

export interface HTTPException {
  detail: any;
}

export function IsHTTPException(o: any): o is HTTPException {
  if (o instanceof Object) {
    return 'detail' in o;
  }
  return false;
}

export interface NodeMetricsResponse {
  node_name: string;
  namespace: string;
  active: boolean;
}

export interface UserProfile {
  username: string;
  user_id: string;
  display_name: string;
  email: string;
  scopes: string[];
}