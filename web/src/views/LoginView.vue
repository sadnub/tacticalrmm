<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex bg-image flex-center">
        <q-card :style="$q.screen.lt.sm ? { width: '80%' } : { width: '30%' }">
          <q-card-section>
            <div class="text-center q-pt-lg">
              <div class="col text-h4 ellipsis">Tactical RMM</div>
            </div>
          </q-card-section>
          <q-card-section>
            <q-form class="q-gutter-md" @submit.prevent="checkCreds">
              <q-input
                v-model="state.username"
                filled
                label="Username"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'This field is required',
                ]"
              />
              <q-input
                v-model="state.password"
                filled
                :type="isPwd ? 'password' : 'text'"
                label="Password"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'This field is required',
                ]"
              >
                <template #append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>
              <div>
                <q-btn
                  label="Login"
                  type="submit"
                  color="primary"
                  class="full-width"
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>
        <!-- 2 factor modal -->
        <q-dialog v-model="prompt2fa" persistent>
          <q-card style="min-width: 400px">
            <q-form @submit.prevent="loginUser">
              <q-card-section class="text-center text-h6"
                >Two-Factor Token</q-card-section
              >

              <q-card-section>
                <q-input
                  v-model="twofactor"
                  autofocus
                  outlined
                  :rules="[
                    (val) =>
                      (val && val.length > 0) || 'This field is required',
                  ]"
                />
              </q-card-section>

              <q-card-actions class="text-primary" align="right">
                <q-btn v-close-popup flat label="Cancel" />
                <q-btn flat label="Submit" type="submit" />
              </q-card-actions>
            </q-form>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
// composition imports
import { ref, onMounted, defineComponent } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useAuthStore } from "stores/auth-store";
import { checkCredentials, login } from "src/api/auth";

export default defineComponent({
  name: "LoginView",
  setup() {
    // setup quasar
    const $q = useQuasar();

    // setup router
    const router = useRouter();

    // setup auth store
    const store = useAuthStore();

    const state = ref({
      username: "",
      password: "",
    });

    const twofactor = ref("");
    const isPwd = ref(true);
    const prompt2fa = ref(false);

    async function checkCreds() {
      try {
        const response = await checkCredentials(state.value);
        if (response.totp === "totp not set") {
          // sign in to setup two factor temporarily
          store.setCredentials(response, state.value.username);
          router.push({ name: "TOTPSetup" });
        } else {
          prompt2fa.value = true;
        }
      } catch (e) {
        console.error(e);
      }
    }

    async function loginUser() {
      try {
        const { token } = await login({
          ...state.value,
          twofactor: twofactor.value,
        });
        store.setCredentials({ token }, state.value.username);
        router.push({ name: "Dashboard" });
      } catch (e) {
        state.value = { username: "", password: "" };
        prompt2fa.value = false;
        console.error(e);
      }
    }

    onMounted(() => $q.dark.set(true));

    return {
      // reactive data
      state,
      prompt2fa,
      isPwd,
      twofactor,

      // methods
      checkCreds,
      loginUser,
    };
  },
});
</script>

<style>
.bg-image {
  background-image: linear-gradient(
    90deg,
    rgba(20, 20, 29, 1) 0%,
    rgba(38, 42, 56, 1) 49%,
    rgba(15, 18, 20, 1) 100%
  );
}
</style>
