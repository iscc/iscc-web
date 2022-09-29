import { createApp } from "vue";
import "./main.scss";
import "@fontsource/readex-pro/400.css";
import App from "./App.vue";
import { tooltip } from "./directives/tooltip";

import "vite/modulepreload-polyfill";

createApp(App).directive("tooltip", tooltip).mount("#app");
