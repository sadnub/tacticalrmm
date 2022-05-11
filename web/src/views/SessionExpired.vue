<template>
  <div class="fixed-center text-center">
    <p class="text-faded">Your session has expired</p>
    <q-btn color="secondary" style="width: 200px" to="/login">Login</q-btn>
  </div>
</template>

<script lang="ts">
// library imports
import { defineComponent, onMounted } from "vue";

// composition imports
import { useAuthStore } from "src/stores/auth-store";

export default defineComponent({
  name: "SessionExpired",
  setup() {
    const store = useAuthStore();

    onMounted(store.clearCredentials);
  },
});
</script>
