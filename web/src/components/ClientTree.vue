<template>
  <div
    v-if="treeLoading"
    class="q-pa-sm q-gutter-sm text-center"
    style="height: 30vh"
  >
    <q-spinner size="40px" color="primary" />
  </div>
  <div v-else class="q-pa-sm q-gutter-sm scroll" style="height: 85vh">
    <q-list dense class="rounded-borders">
      <q-item
        v-ripple
        clickable
        :active="allClientsSelected"
        @click="clearSelectedTree"
      >
        <q-item-section avatar>
          <q-icon name="fas fa-home" />
        </q-item-section>
        <q-item-section>All Clients</q-item-section>
      </q-item>
      <q-tree
        ref="tree"
        v-model:selected="selectedTree"
        :nodes="tree"
        node-key="id"
        no-nodes-label="No Clients"
        selected-color="primary"
        @update:selected="getAgents"
      >
        <template #default-header="props">
          <div class="row items-center">
            <q-icon
              :name="props.node.icon"
              :color="props.node.color"
              class="q-mr-sm"
            />
            <div>
              {{ props.node.label }}
              <q-tooltip :delay="600">
                ID: {{ props.node.id }}<br />
                Agent Count:
                {{
                  props.node.children
                    ? props.node.client.agent_count
                    : props.node.site.agent_count
                }}
              </q-tooltip>
            </div>

            <q-menu context-menu>
              <q-list dense style="min-width: 200px">
                <q-item
                  v-close-popup
                  clickable
                  @click="showEditModal(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="edit" />
                  </q-item-section>
                  <q-item-section>Edit</q-item-section>
                </q-item>
                <q-item
                  v-close-popup
                  clickable
                  @click="showDeleteModal(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="delete" />
                  </q-item-section>
                  <q-item-section>Delete</q-item-section>
                </q-item>

                <q-separator></q-separator>

                <q-item
                  v-if="props.node.children"
                  v-close-popup
                  clickable
                  @click="showAddSiteModal(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="add" />
                  </q-item-section>
                  <q-item-section>Add Site</q-item-section>
                </q-item>

                <q-item
                  v-close-popup
                  clickable
                  @click="showToggleMaintenance(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="construction" />
                  </q-item-section>
                  <q-item-section>{{
                    props.node.color === "green"
                      ? "Disable Maintenance Mode"
                      : "Enable Maintenance Mode"
                  }}</q-item-section>
                </q-item>

                <q-item
                  v-if="props.node.children === undefined"
                  v-close-popup
                  clickable
                  @click="showInstallAgent(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="cloud_download" />
                  </q-item-section>
                  <q-item-section>Install Agent</q-item-section>
                </q-item>

                <q-item
                  v-close-popup
                  clickable
                  @click="showPolicyAdd(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="policy" />
                  </q-item-section>
                  <q-item-section>Assign Automation Policy</q-item-section>
                </q-item>

                <q-item
                  v-close-popup
                  clickable
                  @click="showAlertTemplateAdd(props.node)"
                >
                  <q-item-section side>
                    <q-icon name="error" />
                  </q-item-section>
                  <q-item-section>Assign Alert Template</q-item-section>
                </q-item>

                <q-item v-ripple clickable @click="getURLActions">
                  <q-item-section side>
                    <q-icon name="open_in_new" />
                  </q-item-section>
                  <q-item-section>Run URL Action</q-item-section>
                  <q-item-section side>
                    <q-icon name="keyboard_arrow_right" />
                  </q-item-section>
                  <q-menu auto-close anchor="top end" self="top start">
                    <q-list>
                      <q-item
                        v-for="action in urlActions"
                        :key="action.id"
                        v-close-popup
                        dense
                        clickable
                        @click="
                          openURLAction(
                            props.node.id,
                            action.id,
                            props.node.children ? 'client' : 'site'
                          )
                        "
                      >
                        {{ action.name }}
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-item>

                <q-separator></q-separator>

                <q-item v-close-popup clickable>
                  <q-item-section>Close</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </div>
        </template>
      </q-tree>
    </q-list>
  </div>
</template>

<script lang="ts">
// library imports
import { defineComponent, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { QTreeNode, useQuasar } from "quasar";
import { storeToRefs } from "pinia";

// composition imports
import { useDashboardStore } from "src/stores/dashboard-store";
import { fetchClients, removeClient, removeSite } from "src/api/clients";
import { fetchURLActions, runURLAction } from "src/api/core";
import { bulkMaintenanceMode } from "src/api/agents";
import { notifySuccess, notifyWarning } from "src/utils/notify";

// types
import {
  type Client,
  type SiteNodeType,
  type NodeType,
} from "src/types/clients";
import { type URLActionModelType, type URLAction } from "src/types/core";

// ui imports
import PolicyAdd from "src/components/automation/modals/PolicyAdd.vue";
import ClientsForm from "src/components/clients/ClientsForm.vue";
import SitesForm from "src/components/clients/SitesForm.vue";
import DeleteClient from "src/components/clients/DeleteClient.vue";
import InstallAgent from "src/components/modals/agents/InstallAgent.vue";
import AlertTemplateAdd from "src/components/modals/alerts/AlertTemplateAdd.vue";

export default defineComponent({
  name: "ClientTree",
  setup() {
    // setup quasar
    const $q = useQuasar();

    // setup vue router
    const router = useRouter();

    // setup dashboard store
    const store = useDashboardStore();

    // destructure actions from store
    const { getAgents, clearSelectedTree } = store;

    // destructure store refs
    const { allClientsSelected, clientTreeSort, selectedTree } =
      storeToRefs(store);

    // client tree logic
    const treeLoading = ref(false);
    const tree = ref<QTreeNode[]>([]);

    // TODO: move clients to store and watch to build dynamically
    async function getClientTree() {
      clearSelectedTree();
      treeLoading.value = true;

      try {
        const clients: Client[] = await fetchClients();

        if (clients.length === 0) {
          router.push({ name: "InitialSetup" });
        }

        let nodes = [] as QTreeNode[];
        for (const client of clients) {
          let childSites = [];
          for (const site of client.sites) {
            const siteNode = {
              label: site.name,
              id: site.id,
              raw: `Site|${site.id}`,
              header: "generic",
              icon: "apartment",
              selectable: true,
              site: site,
            } as QTreeNode;

            if (site.maintenance_mode) {
              siteNode.color = "green";
            } else if (site.failing_checks.error) {
              siteNode.color = "negative";
            } else if (site.failing_checks.warning) {
              siteNode.color = "warning";
            }

            childSites.push(siteNode);
          }

          const clientNode = {
            label: client.name,
            id: client.id,
            raw: `Client|${client.id}`,
            header: "root",
            icon: "business",
            children: childSites,
            client: client,
          } as QTreeNode;

          if (client.maintenance_mode) clientNode.color = "green";
          else if (client.failing_checks.error) {
            clientNode.color = "negative";
          } else if (client.failing_checks.warning) {
            clientNode.color = "warning";
          }

          nodes.push(clientNode);
        }

        console.log(nodes);

        // TODO: move sort to separate function so it can watch sort type and do it dynamically
        const sorted = nodes.sort((a, b) =>
          a.label && b.label ? a.label.localeCompare(b.label) : -1
        );
        if (clientTreeSort.value === "alphafail") {
          // move failing clients to the top
          const failing = sorted.filter(
            (i) => i.color === "negative" || i.color === "warning"
          );
          const ok = sorted.filter(
            (i) => i.color !== "negative" && i.color !== "warning"
          );
          tree.value = [...failing, ...ok];
        } else {
          tree.value = sorted;
        }

        console.log(nodes);
      } catch (e) {
        console.error(e);
      }
      treeLoading.value = false;
    }

    onMounted(getClientTree);

    const urlActions = ref<URLAction[]>([]);

    async function getURLActions() {
      $q.loading.show();
      try {
        urlActions.value = await fetchURLActions();

        if (urlActions.value.length === 0) {
          notifyWarning(
            "No URL Actions configured. Go to Settings > Global Settings > URL Actions"
          );
        }
      } catch (e) {
        console.error(e);
      }
      $q.loading.hide();
    }

    async function openURLAction(
      id: number,
      action: number,
      model: URLActionModelType
    ) {
      const data = {
        [model]: id,
        action: action,
      };
      try {
        await runURLAction(data);
      } catch (e) {
        console.error(e);
      }
    }

    function showPolicyAdd(node: NodeType) {
      $q.dialog({
        component: PolicyAdd,
        componentProps: {
          type: node.children ? "client" : "site",
          object: node.children ? node.client : node.site,
        },
      }).onOk(getClientTree);
    }

    function showAddSiteModal(node: SiteNodeType) {
      $q.dialog({
        component: SitesForm,
        componentProps: {
          client: node.id,
        },
      }).onOk(getClientTree);
    }

    function showEditModal(node: NodeType) {
      $q.dialog({
        component: node.children ? ClientsForm : SitesForm,
        componentProps: node.children
          ? { client: node.client }
          : { site: node.site },
      }).onOk(getClientTree);
    }

    function showDeleteModal(node: NodeType) {
      if (
        (node.children && node.client && node.client.agent_count > 0) ||
        (!node.children && node.site && node.site.agent_count > 0)
      ) {
        $q.dialog({
          component: DeleteClient,
          componentProps: {
            object: node.children ? node.client : node.site,
            type: node.children ? "client" : "site",
          },
        }).onOk(getClientTree);
      } else {
        $q.dialog({
          title: "Are you sure?",
          message: `Delete site: ${node.label}.`,
          cancel: true,
          ok: { label: "Delete", color: "negative" },
        }).onOk(async () => {
          $q.loading.show();
          try {
            const result = node.children
              ? await removeClient(node.id)
              : await removeSite(node.id);
            notifySuccess(result);
            getClientTree();
          } catch (e) {
            console.error(e);
          }
          $q.loading.hide();
        });
      }
    }

    function showInstallAgent(node: SiteNodeType) {
      $q.dialog({
        component: InstallAgent,
        componentProps: {
          sitePk: node.id,
        },
      });
    }

    function showAlertTemplateAdd(node: NodeType) {
      $q.dialog({
        component: AlertTemplateAdd,
        componentProps: {
          type: node.children ? "client" : "site",
          object: node.children ? node.client : node.site,
        },
      }).onOk(async () => {
        await getClientTree();
        await getAgents();
      });
    }

    async function showToggleMaintenance(node: NodeType) {
      $q.loading.show();
      const data = {
        id: node.id,
        type: node.raw.split("|")[0],
        action: node.color === "green" ? false : true,
      };

      try {
        const result = await bulkMaintenanceMode(data);
        notifySuccess(result);
        await getClientTree();
        await getAgents();
        // TODO: figure this out
        //this.$store.commit("setRefreshSummaryTab", true);
      } catch (e) {
        console.error(e);
      }

      $q.loading.hide();
    }

    return {
      // reactive
      tree,
      urlActions,
      treeLoading,
      selectedTree,
      allClientsSelected,

      // methods
      clearSelectedTree,
      getAgents,
      getURLActions,
      showToggleMaintenance,
      showAlertTemplateAdd,
      showInstallAgent,
      showDeleteModal,
      showEditModal,
      showAddSiteModal,
      showPolicyAdd,
      openURLAction,
    };
  },
});
</script>
