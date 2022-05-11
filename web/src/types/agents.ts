export type AgentTableTabType = "server" | "workstation" | "mixed";
export type AgentDoubleClickActionType =
  | "editagent"
  | "takecontrol"
  | "remotebg"
  | "urlaction";

export type ClientTreeSortType = "alphafail" | "alpha";

export interface GetAgentsParams {
  monitoring_type?: "server" | "workstation";
  client?: number;
  site?: number;
}

export enum MonitoringType {
  Server = "server",
  Workstation = "workstation",
}

export interface Agent {
  id: number;
  agent_id: string;
  monitoring_type: MonitoringType;
}
