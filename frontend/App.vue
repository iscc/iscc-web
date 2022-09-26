<script setup lang="ts">
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
import HelloWorld from "./components/HelloWorld.vue";
import vueLogo from "./assets/vue.svg";
import viteLogo from "./assets/vite.svg";
</script>

<template lang="pug">
.container
  .row
    .col.text-center
      a(
        href="https://vitejs.dev"
        target="_blank"
        v-tooltip="'Vite'"
      )
        img.logo(:src="viteLogo" alt="Vite logo")
      a(
        href="https://vuejs.org/"
        target="_blank"
        v-tooltip="'Vue'"
      )
        img.logo.vue(:src="vueLogo" alt="Vue logo")
  .row
    .col
      HelloWorld(msg="Vite + Vue")
</template>

<style scoped lang="css">
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
