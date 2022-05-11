import { defineStore } from "pinia";

import {
  GetAgentsParams,
  MonitoringType,
  type Agent,
  type AgentTableTabType,
  type ClientTreeSortType,
  type AgentDoubleClickActionType,
} from "types/agents";

// api
import { fetchAgents } from "api/agents";

export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    // agent table
    agents: [] as Agent[],
    selectedAgent: null as string | null, // agent_id
    agentTableLoading: false,
    defaultAgentTab: null as AgentTableTabType | null, // server | workstation | mixed
    clearSearchWhenSwitching: false,
    agentDoubleClickAction: "editagent" as AgentDoubleClickActionType,
    urlAction: null as number | null,
    agentTableSplitterSize: 300,

    // client/site tree
    selectedTree: "",
    clientTreeSort: "alphafail" as ClientTreeSortType,
    clientTreeSplitterSize: 20,
  }),
  getters: {
    allClientsSelected: (state) => {
      return state.selectedTree === "";
    },
  },
  actions: {
    async getAgents() {
      this.agentTableLoading = true;

      const params: GetAgentsParams = {};
      if (
        this.defaultAgentTab === MonitoringType.Server ||
        this.defaultAgentTab === MonitoringType.Workstation
      ) {
        params.monitoring_type = this.defaultAgentTab;
      }

      if (this.selectedTree.includes("Client")) {
        params.client = parseInt(this.selectedTree.split("|")[1]);
      } else if (this.selectedTree.includes("Site")) {
        params.site = parseInt(this.selectedTree.split("|")[1]);
      }

      try {
        this.agents = await fetchAgents(params);
      } catch (e) {
        console.error(e);
      }

      this.agentTableLoading = false;
    },
    clearSelectedAgent() {
      this.selectedAgent = null;
    },
    clearSelectedTree() {
      this.selectedTree = "";
    },
  },
});
