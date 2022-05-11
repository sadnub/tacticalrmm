import axios from "axios";

// types
import { type User, type Role, type APIKey } from "src/types/accounts";

const baseUrl = "/accounts";

// user api functions
export async function fetchUsers(params = {}) {
  try {
    const { data } = await axios.get(`${baseUrl}/users/`, { params: params });
    return data;
  } catch (e) {
    console.error(e);
  }
}

interface EditUserRequest {
  dark_mode?: boolean;
}

export async function editUser(payload: EditUserRequest): Promise<string> {
  const { data } = await axios.put(`${baseUrl}/users/ui/`, payload);
  return data;
}

// role api function
export async function fetchRoles(params = {}): Promise<Role[]> {
  const { data } = await axios.get(`${baseUrl}/roles/`, { params: params });
  return data;
}

export async function removeRole(id: number) {
  const { data } = await axios.delete(`${baseUrl}/roles/${id}/`);
  return data;
}

export async function saveRole(role: Role): Promise<string> {
  const { data } = await axios.post(`${baseUrl}/roles/`, role);
  return data;
}

export async function editRole(id: number, role: Role): Promise<string> {
  const { data } = await axios.put(`${baseUrl}/roles/${id}/`, role);
  return data;
}

// api key api functions
export async function fetchAPIKeys(params = {}): Promise<APIKey[]> {
  const { data } = await axios.get(`${baseUrl}/apikeys/`, { params: params });
  return data;
}

export async function saveAPIKey(apiKey: APIKey): Promise<string> {
  const { data } = await axios.post(`${baseUrl}/apikeys/`, apiKey);
  return data;
}

export async function editAPIKey(id: number, apiKey: APIKey): Promise<string> {
  const { data } = await axios.put(`${baseUrl}/apikeys/${id}/`, apiKey);
  return data;
}

export async function removeAPIKey(id: number): Promise<string> {
  const { data } = await axios.delete(`${baseUrl}/apikeys/${id}/`);
  return data;
}
