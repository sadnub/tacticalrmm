import axios from "axios";
import { boot } from "quasar/wrappers";
import { Notify } from "quasar";

export const getBaseUrl = () => {
  if (process.env.NODE_ENV === "production" && process.env.DOCKER_BUILD) {
    return window._env_.PROD_URL;
  } else {
    return process.env.API_URL;
  }
};

export default boot(({ /* app, */ router, store }) => {
  axios.interceptors.request.use(
    function (config) {
      config.baseURL = getBaseUrl();
      const token = store.state.value.auth.token;
      if (token != null) {
        config.headers.Authorization = `Token ${token}`;
      }
      return config;
    },
    function (err) {
      return Promise.reject(err);
    }
  );

  axios.interceptors.response.use(
    function (response) {
      return response;
    },
    async function (error) {
      let text;

      if (!error.response) {
        text = error.message;
      }
      // unauthorized
      else if (error.response.status === 401) {
        router.push({ path: "/expired" });
      }
      // perms
      else if (error.response.status === 403) {
        // don't notify user if method is GET
        if (error.config.method === "get" || error.config.method === "patch")
          return Promise.reject({ ...error });
        text = error.response.data.detail;
      }
      // catch all for other 400 error messages
      else if (error.response.status >= 400 && error.response.status < 500) {
        if (error.config.responseType === "blob") {
          text = (await error.response.data.text()).replace(/^"|"$/g, "");
        } else if (error.response.data.non_field_errors) {
          text = error.response.data.non_field_errors[0];
        } else {
          if (typeof error.response.data === "string") {
            text = error.response.data;
          } else if (typeof error.response.data === "object") {
            const [key, value] = Object.entries(error.response.data)[0];
            text = key + ": " + value[0];
          }
        }
      }

      if (text || error.response) {
        Notify.create({
          color: "negative",
          message: text ? text : "",
          caption: error.response
            ? error.response.status + ": " + error.response.statusText
            : "",
          timeout: 2500,
        });
      }

      return Promise.reject({ ...error });
    }
  );
});
