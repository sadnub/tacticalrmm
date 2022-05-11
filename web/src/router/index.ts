import { route } from "quasar/wrappers";
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from "vue-router";

import routes from "./routes";

import { useAuthStore } from "stores/auth-store";

export default route(function (/* { store } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach((to, from, next) => {
    const store = useAuthStore();

    if (to.meta.requireAuth && !store.loggedIn) {
      next({
        name: "Login",
      });
    } else if (to.meta.requiresVisitor && store.loggedIn) {
      next({
        name: "Dashboard",
      });
    } else {
      next();
    }
  });

  return Router;
});
