import axios from "axios";
import { openURL } from "quasar";

// types
import { type URLAction } from "src/types/core";

const baseUrl = "/core";

export async function fetchCustomFields(params = {}) {
  try {
    const { data } = await axios.get(`${baseUrl}/customfields/`, {
      params: params,
    });
    return data;
  } catch (e) {
    console.error(e);
  }
}

export async function fetchDashboardInfo(params = {}) {
  const { data } = await axios.get(`${baseUrl}/dashinfo/`, { params: params });
  return data;
}

export async function fetchURLActions(params = {}): Promise<URLAction[]> {
  const { data } = await axios.get(`${baseUrl}/urlaction/`, {
    params: params,
  });
  return data;
}

interface RunURLActionRequestType {
  agent?: number;
  client?: number;
  site?: number;
  action: number;
}

export async function runURLAction(payload: RunURLActionRequestType) {
  try {
    const { data } = await axios.patch(`${baseUrl}/urlaction/run/`, payload);
    openURL(data);
  } catch (e) {
    console.error(e);
  }
}

export async function fetchVersion(params = {}): Promise<string> {
  const { data } = await axios.get(`${baseUrl}/version/`, { params: params });
  return data;
}
