<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-grey-9 text-white">
      <q-banner
        v-if="needRefresh"
        inline-actions
        class="bg-red text-white text-center"
      >
        You are viewing an outdated version of this page.
        <q-btn color="dark" icon="refresh" label="Refresh" @click="reload" />
      </q-banner>
      <q-toolbar>
        <!-- TODO: Figure out if refresh button is needed -->
        <q-btn v-if="$route.name === 'Dashboard'" dense flat icon="refresh" />
        <q-btn
          v-else
          dense
          flat
          icon="dashboard"
          @click="$router.push({ name: 'Dashboard' })"
        >
          <q-tooltip>Back to Dashboard</q-tooltip>
        </q-btn>
        <q-toolbar-title>
          Tactical RMM<span class="text-overline q-ml-sm"
            >v{{ currentTRMMVersion }}</span
          >
          <span
            v-if="
              latestTRMMVersion !== 'error' &&
              currentTRMMVersion !== latestTRMMVersion
            "
            class="text-overline q-ml-md"
            ><q-badge color="warning"
              ><a :href="latestReleaseUrl" target="_blank"
                >v{{ latestTRMMVersion }} available</a
              ></q-badge
            ></span
          >
        </q-toolbar-title>

        <!-- temp dark mode toggle -->
        <q-toggle
          v-model="darkMode"
          class="q-mr-sm"
          checked-icon="nights_stay"
          unchecked-icon="wb_sunny"
        />

        <!-- Devices Chip -->
        <q-chip class="cursor-pointer">
          <q-avatar size="md" icon="devices" color="primary" />
          <q-tooltip :delay="600" anchor="top middle" self="top middle"
            >Agent Count</q-tooltip
          >
          {{ serverCount + workstationCount }}
          <q-menu>
            <q-list dense>
              <q-item-label header>Servers</q-item-label>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="fa fa-server" size="sm" color="primary" />
                </q-item-section>

                <q-item-section no-wrap>
                  <q-item-label>Total: {{ serverCount }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="power_off" size="sm" color="negative" />
                </q-item-section>

                <q-item-section no-wrap>
                  <q-item-label>Offline: {{ serverOfflineCount }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item-label header>Workstations</q-item-label>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="computer" size="sm" color="primary" />
                </q-item-section>

                <q-item-section no-wrap>
                  <q-item-label>Total: {{ workstationCount }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="power_off" size="sm" color="negative" />
                </q-item-section>

                <q-item-section no-wrap>
                  <q-item-label
                    >Offline: {{ workstationOfflineCount }}</q-item-label
                  >
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-chip>
        <!--TODO: -->
        <!--<AlertsIcon />-->

        <q-btn-dropdown flat no-caps stretch :label="username">
          <q-list>
            <!-- TODO: -->
            <!-- <q-item
              v-ripple
              v-close-popup
              clickable
              @click="showUserPreferences"
            >
              <q-item-section>
                <q-item-label>Preferences</q-item-label>
              </q-item-section>
            </q-item> -->
            <q-item to="/expired" exact>
              <q-item-section>
                <q-item-label>Logout</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>
<script lang="ts">
// composition imports
import { computed, onMounted, onBeforeUnmount, defineComponent } from "vue";
import { useQuasar } from "quasar";
import { useAuthStore } from "stores/auth-store";
import { useMainStore } from "stores/main-store";
import { storeToRefs } from "pinia";
import { editUser } from "api/accounts";

// ui imports
// import AlertsIcon from "components/AlertsIcon";
// import UserPreferences from "components/modals/coresettings/UserPreferences";

export default defineComponent({
  name: "MainLayout",
  components: {
    /*AlertsIcon*/
  },
  setup() {
    // setup stores
    const authStore = useAuthStore();
    const mainStore = useMainStore();

    // setup quasar
    const $q = useQuasar();

    const darkMode = computed({
      get: () => {
        return $q.dark.isActive;
      },
      set: async (value) => {
        await editUser({ dark_mode: value });
        $q.dark.set(value);
      },
    });

    const {
      ws,
      serverCount,
      serverOfflineCount,
      workstationCount,
      workstationOfflineCount,
      currentTRMMVersion,
      latestTRMMVersion,
      needRefresh,
      latestReleaseUrl,
    } = storeToRefs(mainStore);

    const { checkVersion, reload, setupWS } = mainStore;
    const { username } = storeToRefs(authStore);

    // function showUserPreferences() {
    //   $q.dialog({
    //     component: UserPreferences,
    //   }); //.onOk(() => store.dispatch("getDashInfo")); Make this send a command server through WS
    // }

    onMounted(() => {
      setupWS();
    });

    onBeforeUnmount(() => {
      ws.value.close();
    });

    return {
      // reactive data
      serverCount,
      serverOfflineCount,
      workstationCount,
      workstationOfflineCount,
      latestReleaseUrl,
      currentTRMMVersion,
      latestTRMMVersion,
      username,
      needRefresh,
      darkMode,

      // methods
      //showUserPreferences,
      reload,
      checkVersion,
    };
  },
});
</script>
