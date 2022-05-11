<template>
  <q-page>
    <!--<FileBar /> -->
    <q-splitter
      v-model="store.clientTreeSplitterSize"
      :style="{ height: `${$q.screen.height - 50 - 40}px` }"
    >
      <template #before>
        <client-tree />
      </template>

      <template #after>
        <q-splitter
          v-model="store.agentTableSplitterSize"
          reverse
          unit="px"
          horizontal
          after-class="hide-scrollbar"
          before-class="hide-scrollbar"
          emit-immediately
        >
          <template #before>
            <!-- <div class="row">
              <q-tabs
                v-model="tab"
                dense
                no-caps
                inline-label
                class="text-grey"
                active-color="primary"
                indicator-color="primary"
                align="left"
                narrow-indicator
              >
                <q-tab name="server" icon="fas fa-server" label="Servers" />
                <q-tab
                  name="workstation"
                  icon="computer"
                  label="Workstations"
                />
                <q-tab name="mixed" label="Mixed" />
              </q-tabs>
              <q-space />
              <q-input
                v-model="search"
                style="width: 450px"
                label="Search"
                dense
                outlined
                clearable
                class="q-pr-md q-pb-xs"
                @clear="clearFilter"
              >
                <template #prepend>
                  <q-icon name="search" color="primary" />
                </template>
                <template #after>
                  <q-btn
                    round
                    dense
                    flat
                    icon="filter_alt"
                    :color="isFilteringTable ? 'green' : ''"
                  >
                    <q-menu>
                      <q-list dense>
                        <q-item-label header>Filter Agent Table</q-item-label>

                        <q-item>
                          <q-item-section side>
                            <q-checkbox v-model="filterChecksFailing" />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Checks Failing</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-checkbox v-model="filterPatchesPending" />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Patches Pending</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-checkbox v-model="filterActionsPending" />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Actions Pending</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-checkbox v-model="filterRebootNeeded" />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Reboot Needed</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item-label header>Availability</q-item-label>

                        <q-item>
                          <q-item-section side>
                            <q-radio v-model="filterAvailability" val="all" />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Show All Agents</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-radio
                              v-model="filterAvailability"
                              val="online"
                            />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Show Online Only</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-radio
                              v-model="filterAvailability"
                              val="offline"
                            />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Show Offline Only</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-radio
                              v-model="filterAvailability"
                              val="overdue"
                            />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label>Show Overdue Only</q-item-label>
                          </q-item-section>
                        </q-item>

                        <q-item>
                          <q-item-section side>
                            <q-radio
                              v-model="filterAvailability"
                              val="offline_30days"
                            />
                          </q-item-section>

                          <q-item-section>
                            <q-item-label
                              >Show Offline for over 30 days</q-item-label
                            >
                          </q-item-section>
                        </q-item>
                      </q-list>

                      <div class="row no-wrap q-pa-md">
                        <div class="column">
                          <q-btn
                            v-close-popup
                            label="Apply"
                            color="primary"
                            @click="applyFilter"
                          />
                        </div>
                        <q-space />
                        <div class="column">
                          <q-btn label="Clear" @click="clearFilter" />
                        </div>
                      </div>
                    </q-menu>
                  </q-btn>
                </template>
              </q-input>
            </div> -->
            <!-- <AgentTable
              :agents="filteredAgents"
              :columns="columns"
              :search="search"
              :visible-columns="visibleColumns"
            /> -->
          </template>
          <template #separator>
            <q-avatar
              color="primary"
              text-color="white"
              size="20px"
              icon="drag_indicator"
            />
          </template>
          <template #after>
            <!-- <SubTableTabs /> -->
          </template>
        </q-splitter>
      </template>
    </q-splitter>

    <!-- TODO: convert to quasar plugin dialog -->
    <!-- <q-dialog v-model="showInstallAgentModal" @hide="closeInstallAgent">
      <InstallAgent :sitepk="parseInt(sitePk)" @close="closeInstallAgent" />
    </q-dialog> -->
  </q-page>
</template>

<script lang="ts">
// library imports
import { defineComponent } from "vue";

// composition imports
import { useDashboardStore } from "stores/dashboard-store";

// ui imports
import ClientTree from "src/components/ClientTree.vue";
//import FileBar from "src/components/FileBar";
//import AgentTable from "src/components/AgentTable";
//import SubTableTabs from "src/components/SubTableTabs";

export default defineComponent({
  name: "DashboardView",
  components: {
    ClientTree,
    //FileBar,
    //AgentTable,
    //SubTableTabs,
  },
  // allow child components to refresh table
  // TODO: replace this with websockets subscriptions
  // provide() {
  //   return {
  //     refreshDashboard: (clearTreeSelected, clearSubTable) => {
  //       if (clearSubTable) this.$store.commit("destroySubTable");

  //       this.$store.dispatch("refreshDashboard", clearTreeSelected);
  //     },
  //   };
  // },
  setup() {
    // setup dashboard store
    const store = useDashboardStore();

    return {
      store,
    };
  },
  data() {
    return {
      // TODO: Move to Agents Table
      // search: "",
      // filterTextLength: 0,
      // filterAvailability: "all",
      // filterPatchesPending: false,
      // filterActionsPending: false,
      // filterChecksFailing: false,
      // filterRebootNeeded: false,
      // columns: [
      //   {
      //     name: "smsalert",
      //     align: "left",
      //   },
      //   {
      //     name: "emailalert",
      //     align: "left",
      //   },
      //   {
      //     name: "dashboardalert",
      //     align: "left",
      //   },
      //   {
      //     name: "plat",
      //     label: "",
      //     field: "plat",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "checks-status",
      //     align: "left",
      //     field: "checks",
      //     sortable: true,
      //     sort: (a, b) =>
      //       parseInt(b.failing) - parseInt(a.failing) ||
      //       parseInt(b.warning) - parseInt(a.warning) ||
      //       parseInt(b.info) - parseInt(a.info),
      //   },
      //   {
      //     name: "client_name",
      //     label: "Client",
      //     field: "client_name",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "site_name",
      //     label: "Site",
      //     field: "site_name",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "hostname",
      //     label: "Hostname",
      //     field: "hostname",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "description",
      //     label: "Description",
      //     field: "description",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "user",
      //     label: "User",
      //     field: "logged_username",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "italic",
      //     field: "italic",
      //   },
      //   {
      //     name: "patchespending",
      //     field: "has_patches_pending",
      //     align: "left",
      //     sortable: true,
      //   },
      //   {
      //     name: "pendingactions",
      //     field: "pending_actions_count",
      //     align: "left",
      //     sortable: true,
      //   },
      //   {
      //     name: "needs_reboot",
      //     field: "needs_reboot",
      //     align: "left",
      //     sortable: true,
      //   },
      //   {
      //     name: "agentstatus",
      //     field: "status",
      //     align: "left",
      //     sortable: true,
      //   },
      //   {
      //     name: "last_seen",
      //     label: "Last Response",
      //     field: "last_seen",
      //     sortable: true,
      //     align: "left",
      //   },
      //   {
      //     name: "boot_time",
      //     label: "Boot Time",
      //     field: "boot_time",
      //     sortable: true,
      //     align: "left",
      //   },
      // ],
      // visibleColumns: [
      //   "smsalert",
      //   "plat",
      //   "emailalert",
      //   "dashboardalert",
      //   "checks-status",
      //   "client_name",
      //   "site_name",
      //   "hostname",
      //   "description",
      //   "user",
      //   "patchespending",
      //   "pendingactions",
      //   "agentstatus",
      //   "needs_reboot",
      //   "last_seen",
      //   "boot_time",
      // ],
    };
  },
  computed: {
    // isFilteringTable() {
    //   return (
    //     this.filterPatchesPending ||
    //     this.filterActionsPending ||
    //     this.filterChecksFailing ||
    //     this.filterRebootNeeded ||
    //     this.filterAvailability !== "all"
    //   );
    // },
  },
  watch: {
    // TODO: Move to Client Tree
    // selectedTree() {
    //   if (this.clearSearchWhenSwitching) this.clearFilter();
    // },
    // TODO: Move to Agents Table
    // tab() {
    //   this.$store.dispatch("loadAgents");
    // },
    // search(newVal) {
    //   if (newVal === "") this.clearFilter();
    //   else if (newVal.length < this.filterTextLength) this.clearFilter();
    // },
  },
  methods: {
    // clearFilter() {
    //   this.filterTextLength = 0;
    //   this.filterPatchesPending = false;
    //   this.filterRebootNeeded = false;
    //   this.filterChecksFailing = false;
    //   this.filterActionsPending = false;
    //   this.filterAvailability = "all";
    //   this.search = "";
    // },
    // applyFilter() {
    //   // clear search if availability changes to all
    //   if (
    //     this.filterAvailability === "all" &&
    //     (this.search.includes("is:online") ||
    //       this.search.includes("is:offline") ||
    //       this.search.includes("is:expired") ||
    //       this.search.includes("is:overdue"))
    //   )
    //     this.clearFilter();
    //   // don't apply filter if nothing is being filtered
    //   if (!this.isFilteringTable) return;
    //   let filterText = "";
    //   if (this.filterPatchesPending) {
    //     filterText += "is:patchespending ";
    //   }
    //   if (this.filterActionsPending) {
    //     filterText += "is:actionspending ";
    //   }
    //   if (this.filterChecksFailing) {
    //     filterText += "is:checksfailing ";
    //   }
    //   if (this.filterRebootNeeded) {
    //     filterText += "is:rebootneeded ";
    //   }
    //   if (this.filterAvailability !== "all") {
    //     if (this.filterAvailability === "online") {
    //       filterText += "is:online ";
    //     } else if (this.filterAvailability === "offline") {
    //       filterText += "is:offline ";
    //     } else if (this.filterAvailability === "offline_30days") {
    //       filterText += "is:expired ";
    //     } else if (this.filterAvailability === "overdue") {
    //       filterText += "is:overdue ";
    //     }
    //   }
    //   this.search = filterText;
    //   this.filterTextLength = filterText.length - 1;
    // },
  },
});
</script>

<style>
.my-menu-link {
  color: white;
  background: lightgray;
}
</style>
