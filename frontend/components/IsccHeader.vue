<script setup lang="ts">
import isccLogo from "../assets/iscc-logo-extended-black.svg?raw";
import punchline from "../assets/iscc-punchline.svg";
</script>

<template lang="pug">
.container
  .row
    .col(v-html="isccLogo")
  .row
    .col
      img.punchline(:src="punchline" alt="The DNA of your digital content")
</template>

<style scoped lang="scss">
.punchline {
  width: 100%;
}
</style>
