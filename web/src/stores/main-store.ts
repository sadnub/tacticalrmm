import { defineStore } from "pinia";
import { useAuthStore } from "stores/auth-store";
import { useDashboardStore } from "stores/dashboard-store";
import { getBaseUrl } from "src/boot/axios";
import { fetchVersion } from "api/core";
import { Dark, LoadingBar } from "quasar";
import {
  type AgentDoubleClickActionType,
  type AgentTableTabType,
  type ClientTreeSortType,
} from "types/agents";

interface WSAgentCount {
  message: "agent_count";
  server_offline_count: number;
  workstation_offline_count: number;
  server_count: number;
  workstation_count: number;
}

interface WSDashboardInfo {
  message: "dashboard_info";
  trmm_version: string;
  latest_trmm_version: string;
  dark_mode: boolean;
  show_community_scripts: boolean;
  dbl_click_action: AgentDoubleClickActionType;
  default_agent_tbl_tab: AgentTableTabType;
  url_action: number;
  client_tree_sort: ClientTreeSortType;
  client_tree_splitter: number;
  loading_bar_color: string;
  clear_search_when_switching: boolean;
  hosted: boolean;
  date_format: string | null;
  default_date_format: string;
}

export const useMainStore = defineStore("main", {
  state: () => ({
    ws: {} as WebSocket,
    currentTRMMVersion: undefined as string | undefined,
    latestTRMMVersion: undefined as string | undefined,
    needRefresh: false,
    serverCount: 0,
    serverOfflineCount: 0,
    workstationCount: 0,
    workstationOfflineCount: 0,
    hosted: false,
    dateFormat: "MMM-DD-YYYY - HH:mm",
    showCommunityScripts: true,
  }),
  getters: {
    latestReleaseUrl: (state) => {
      return `https://github.com/amidaware/tacticalrmm/releases/tag/v${state.latestTRMMVersion}`;
    },
    wsUrl: (/* state */) => {
      const authStore = useAuthStore();
      const token = authStore.token;
      const wsBaseUrl = getBaseUrl().split("://")[1];

      const proto =
        process.env.NODE_ENV === "production" || process.env.DOCKER_BUILD
          ? "wss"
          : "ws";

      return `${proto}://${wsBaseUrl}/ws/?access_token=${token}`;
    },
  },
  actions: {
    setupWS() {
      console.log("Starting websocket");

      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log("Connected to ws");
      };

      this.ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.message === "agent_count") {
          this.handleAgentCount(data);
        } else if (data.message === "dashboard_info") {
          this.handleDashboardInfo(data);
        }
      };

      this.ws.onclose = (e) => {
        try {
          console.log(`Closed code: ${e.code}`);
          console.log("Retrying websocket connection...");
          setTimeout(() => {
            this.setupWS();
          }, 3 * 1000);
        } catch (e) {
          console.log("Websocket connection closed");
        }
      };

      this.ws.onerror = () => {
        console.log("There was an error with the Websocket connection");
        this.ws.close();
      };
    },
    handleAgentCount(data: WSAgentCount) {
      this.serverCount = data.server_count;
      this.workstationCount = data.workstation_count;
      this.serverOfflineCount = data.server_offline_count;
      this.workstationOfflineCount = data.workstation_offline_count;
    },
    handleDashboardInfo(data: WSDashboardInfo) {
      const dashboardStore = useDashboardStore();

      Dark.set(data.dark_mode);
      LoadingBar.setDefaults({ color: data.loading_bar_color });

      this.currentTRMMVersion = data.trmm_version;
      this.latestTRMMVersion = data.latest_trmm_version;
      this.hosted = data.hosted;
      this.showCommunityScripts = data.show_community_scripts;

      dashboardStore.clearSearchWhenSwitching =
        data.clear_search_when_switching;
      dashboardStore.defaultAgentTab = data.default_agent_tbl_tab;
      dashboardStore.clientTreeSort = data.client_tree_sort;
      dashboardStore.clientTreeSplitterSize = data.client_tree_splitter;
      dashboardStore.agentDoubleClickAction = data.dbl_click_action;
      dashboardStore.urlAction = data.url_action;

      if (data.date_format && data.date_format !== "")
        this.dateFormat = data.date_format;
      else this.dateFormat = data.default_date_format;
    },
    async checkVersion() {
      try {
        const version = await fetchVersion();

        if (localStorage.getItem("rmmver")) {
          if (localStorage.getItem("rmmver") === version) {
            return;
          } else {
            localStorage.setItem("rmmver", "0.0.1");
            this.needRefresh = true;
          }
        } else {
          localStorage.setItem("rmmver", version);
          return;
        }
      } catch (e) {
        console.error(e);
      }
    },
    reload() {
      localStorage.removeItem("rmmver");
      location.reload();
    },
  },
});
