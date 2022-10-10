import { createApp } from "vue";
import "./main.scss";
import "@fontsource/readex-pro";
import "@fontsource/jetbrains-mono";
import App from "./App.vue";
import { tooltip } from "./directives/tooltip";

import "vite/modulepreload-polyfill";

createApp(App).directive("tooltip", tooltip).mount("#app");
