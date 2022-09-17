<script setup lang="ts">
import { ref } from "vue";

defineProps<{ msg: string }>();

const count = ref(0);
</script>

<template lang="pug">
div
  h1 {{ msg }}

  .card
    button(type="button" @click="count++") count is {{ count }}
    button(type="button" @click="count = count + 10") +10
    p
      | Edit&nbsp;
      code frontend/components/HelloWorld.vue&nbsp;
      | to test HMR

  p
    | Check out&nbsp;
    a(href="https://vuejs.org/guide/quick-start.html#local" target="_blank") create-vue
    | , the official Vue + Vite starter
  p
    | Install&nbsp;
    a(href="https://github.com/johnsoncodehk/volar" target="_blank") Volar
    | &nbsp;in your IDE for a better DX
  p.read-the-docs Click on the Vite and Vue logos to learn more
</template>

<style scoped lang="css">
.read-the-docs {
  color: #888;
}
</style>
