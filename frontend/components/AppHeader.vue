<script setup lang="ts">
// Navy top bar: brand signature, product name and the developer exits.
import isccLogo from "../assets/iscc-logo-white-coral.svg";
import UiIcon from "./UiIcon.vue";
</script>

<template lang="pug">
header.app-header.grain.on-dark
  .container-xl.d-flex.align-items-center.justify-content-between.py-3
    .d-flex.align-items-center.gap-3
      img.logo(:src="isccLogo" alt="ISCC")
      .divider.d-none.d-sm-block
      span.product.d-none.d-sm-inline GENERATOR
    .d-flex.align-items-center.gap-4
      a.quiet-link.d-none.d-md-inline(
        href="https://iscc.codes"
        target="_blank"
        rel="noopener"
      ) What is an ISCC?
      a.iscc-btn.iscc-btn--secondary.iscc-btn--compact(href="/docs" target="_blank")
        UiIcon(name="code" :size="14")
        span API Docs
</template>

<style scoped lang="scss">
.app-header {
  background-color: var(--iscc-deep-navy);

  // The SVG master carries its clear space in the viewBox; 2.5rem tall = 144 px wide.
  .logo {
    height: 2.5rem;
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
}
</style>
