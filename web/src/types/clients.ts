interface FailChecksType {
  error: boolean;
  warning: boolean;
}

export interface Client {
  id: number;
  name: string;
  maintenance_mode: boolean;
  failing_checks: FailChecksType;
  sites: Site[];
  agent_count: number;
}

export interface Site {
  id: number;
  name: string;
  maintenance_mode: boolean;
  failing_checks: FailChecksType;
  agent_count: number;
}

export interface SiteNodeType {
  label: string;
  id: number;
  raw: string;
  color?: "green" | "negative" | "warning";
  header: "generic";
  icon: "apartment";
  selectable: true;
  site: Site;
}

export interface NodeType {
  label: string;
  id: number;
  raw: string;
  color?: "green" | "negative" | "warning";
  header: string;
  icon: string;
  children?: SiteNodeType[];
  client?: Client;
  site?: Site;
}
