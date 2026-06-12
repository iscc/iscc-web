<script setup lang="ts">
// Navy top bar: brand mark, product name and the developer exits.
import isccLogo from "../assets/iscc-logo-white.png";
import UiIcon from "./UiIcon.vue";
</script>

<template lang="pug">
header.app-header.grain
  .container-xl.d-flex.align-items-center.justify-content-between.py-3
    .d-flex.align-items-center.gap-3
      img.logo(:src="isccLogo" alt="ISCC logo")
      .divider
      span.product GENERATOR
    .d-flex.align-items-center.gap-4
      a.quiet-link.d-none.d-md-inline(
        href="https://iscc.codes"
        target="_blank"
        rel="noopener"
      ) What is an ISCC?
      a.docs-btn(href="/docs" target="_blank")
        UiIcon(name="code" :size="14")
        span API Docs
</template>

<style scoped lang="scss">
.app-header {
  background-color: var(--iscc-deep-navy);

  .logo {
    height: 1.9rem;
    width: auto;
    display: block;
  }

  .divider {
    width: 3px;
    height: 1.6rem;
    background: var(--iscc-bright-yellow);
    border-radius: 1px;
  }

  .product {
    color: #ffffff;
    font-weight: 300;
    letter-spacing: 0.1em;
    font-size: 1.05rem;
  }

  .quiet-link {
    color: rgba(255, 255, 255, 0.78);
    font-size: 0.85rem;
    font-weight: 300;
    text-decoration: none;

    &:hover {
      color: #ffffff;
    }
  }

  .docs-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    color: #ffffff;
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 0.5rem;
    padding: 0.45rem 0.8rem;

    &:hover {
      border-color: rgba(255, 255, 255, 0.7);
      color: #ffffff;
    }
  }
}
</style>
