<script setup lang="ts"></script>

<template lang="pug">
.footer
  span Copyright © 2022 ISCC Foundation
  span &nbsp;|&nbsp;
  a.link-secondary(href="https://iscc.foundation/privacy/" target="_blank") Privacy Policy
  span &nbsp;|&nbsp;
  a.link-secondary(href="https://iscc.foundation/cookies" target="_blank") Cookie Policy
  span &nbsp;|&nbsp;
  a.link-secondary(href="https://iscc.foundation/imprint" target="_blank") Imprint
  span &nbsp;|&nbsp;
  a.link-secondary(href="https://iscc.foundation/disclaimer" target="_blank") Disclaimer
  span &nbsp;|&nbsp;
  a.link-secondary(href="/docs" target="_blank") API Docs
  span &nbsp;|&nbsp;
  a.link-secondary(href="https://github.com/iscc/iscc-web" target="_blank") Source Code
</template>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions";
@import "~bootstrap/scss/_variables";
@import "~bootstrap/scss/_mixins";

.footer {
  border: $card-border-width solid $card-border-color;
  @include border-radius($card-border-radius);
  background-color: $card-cap-bg;
  padding: $card-cap-padding-y $card-cap-padding-x;
  color: $card-cap-color;
}
</style>
