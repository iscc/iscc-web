// App entry point: fonts, styles, JSON highlighting and the root Vue app.
import { createApp } from "vue";
import "./main.scss";
import "@fontsource/readex-pro/300.css";
import "@fontsource/readex-pro";
import "@fontsource/readex-pro/600.css";
import "@fontsource/readex-pro/700.css";
import "@fontsource/jetbrains-mono/300.css";
import "@fontsource/jetbrains-mono";
import "@fontsource/jetbrains-mono/500.css";
import "@fontsource/jetbrains-mono/700.css";
import App from "./App.vue";

import "vite/modulepreload-polyfill";

import hljs from "highlight.js/lib/core";
import json from "highlight.js/lib/languages/json";
import hljsVuePlugin from "@highlightjs/vue-plugin";

hljs.registerLanguage("json", json);

createApp(App).use(hljsVuePlugin).mount("#app");
