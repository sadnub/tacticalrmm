import { defineStore } from "pinia";
import type { LoginResponse } from "types/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    username: localStorage.getItem("user_name") || undefined,
    token: localStorage.getItem("access_token") || undefined,
  }),
  getters: {
    loggedIn: (state) => {
      return state.token !== undefined;
    },
  },
  actions: {
    setCredentials({ token }: LoginResponse, username: string) {
      localStorage.setItem("access_token", token);
      localStorage.setItem("user_name", username);
      this.token = token;
      this.username = username;
    },
    clearCredentials() {
      if (this.loggedIn) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_name");
        this.token = undefined;
        this.username = undefined;
      }
    },
  },
});
