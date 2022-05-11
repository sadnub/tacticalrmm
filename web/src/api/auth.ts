import axios from "axios";

interface CheckCredentialsRequest {
  username: string;
  password: string;
}

interface CheckCredentialsResponse {
  username: string;
  token: string;
  totp?: string;
}

export async function checkCredentials(
  payload: CheckCredentialsRequest
): Promise<CheckCredentialsResponse> {
  const { data } = await axios.post("/checkcreds/", payload);
  return data;
}

interface LoginRequest {
  username: string;
  password: string;
  twofactor: string;
}

interface LoginResponse {
  token: string;
}

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const { data } = await axios.post("/login/", payload);
  return data;
}

export async function logout() {
  const { data } = await axios.post("/logout/");
  return data;
}

interface TOTPSetupResponse {
  totp_key: string;
  qr_url: string;
}

export async function setupTOTP(): Promise<TOTPSetupResponse> {
  const { data } = await axios.post("/accounts/users/setup_totp/");
  return data;
}
