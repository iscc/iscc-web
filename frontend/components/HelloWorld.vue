<script setup lang="ts">
import { ref } from "vue";

defineProps<{ msg: string }>();

const count = ref(0);
</script>

<template lang="pug">
.card
  .card-body
    h5.card-title {{ msg }}

    .my-3
      button.btn.btn-primary(type="button" @click="count++") count is {{ count }}
      button.btn.btn-secondary.ms-2(type="button" @click="count = count + 10") +10

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

    p.mb-0.text-secondary Click on the Vite and Vue logos to learn more
</template>

<style scoped lang="css"></style>
