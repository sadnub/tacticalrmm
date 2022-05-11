<template>
  <div class="q-pa-md">
    <div class="row">
      <div class="col"></div>
      <div class="col">
        <q-card>
          <q-card-section class="row items-center">
            <div class="text-h6">Setup 2-Factor</div>
          </q-card-section>
          <q-card-section v-if="qrUrl">
            <p>
              Scan the QR Code with your authenticator app and then click Finish
              to be redirected back to the signin page. If you navigate away
              from this page you 2FA signin will need to be reset!
            </p>
            <qrcode-vue :value="qrUrl" :size="200" level="H" />
          </q-card-section>
          <q-card-section v-if="totpKey">
            <p>
              You can also use the below code to configure the authenticator
              manually.
            </p>
            <p>{{ totpKey }}</p>
          </q-card-section>
          <q-card-actions align="center">
            <q-btn
              label="Finish"
              color="primary"
              class="full-width"
              @click="logoutUser"
            />
          </q-card-actions>
        </q-card>
      </div>
      <div class="col"></div>
    </div>
  </div>
</template>

<script lang="ts">
// composition imports
import { ref, onMounted, onUnmounted, defineComponent } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useAuthStore } from "src/stores/auth-store";
import { setupTOTP, logout } from "api/auth";

// ui components
import QrcodeVue from "qrcode.vue";

export default defineComponent({
  name: "TOTPSetupView",
  components: { QrcodeVue },
  setup() {
    // setup quasar
    const $q = useQuasar();

    // setup router
    const router = useRouter();

    // setup auth store
    const store = useAuthStore();

    // totp setup logic
    const totpKey = ref("");
    const qrUrl = ref("");
    const clearToken = ref(false);

    async function getQRCodeData() {
      $q.loading.show();

      try {
        const { totp_key, qr_url } = await setupTOTP();
        totpKey.value = totp_key;
        qrUrl.value = qr_url;
        clearToken.value = true;
      } catch (e) {
        console.error(e);
        router.push({ name: "Login" });
      }

      $q.loading.hide();
    }

    async function logoutUser() {
      $q.loading.show();

      try {
        await logout();
      } catch (e) {
        console.error(e);
      }

      store.clearCredentials();
      clearToken.value = false;
      $q.loading.hide();
      router.push({ name: "Login" });
    }

    onMounted(getQRCodeData);

    onUnmounted(() => {
      if (clearToken.value) {
        logoutUser();
      }
    });

    return {
      totpKey,
      qrUrl,

      // methods
      logoutUser,
    };
  },
});
</script>
