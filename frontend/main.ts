import { createApp } from "vue";
import "./main.scss";
import "@fontsource/readex-pro/300.css";
import "@fontsource/readex-pro";
import "@fontsource/readex-pro/600.css";
import "@fontsource/jetbrains-mono";
import App from "./App.vue";
import { tooltip } from "./directives/tooltip";

import "vite/modulepreload-polyfill";

import hljs from "highlight.js/lib/core";
import json from "highlight.js/lib/languages/json";
import hljsVuePlugin from "@highlightjs/vue-plugin";

hljs.registerLanguage("json", json);

createApp(App).use(hljsVuePlugin).directive("tooltip", tooltip).mount("#app");
