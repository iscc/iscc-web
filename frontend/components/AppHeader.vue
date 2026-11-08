<script setup lang="ts">
// Navy top bar: the ISCC generator project logo (the ISCC signature alone on phones, where the
// lockup would be too small) and the developer exits.
import isccLogo from "../assets/iscc-logo-white-coral.svg";
import productLockup from "../assets/iscc-generator-white-coral.svg";
import UiIcon from "./UiIcon.vue";
</script>

<template lang="pug">
header.app-header.grain.on-dark
  .container-xl.d-flex.align-items-center.justify-content-between.py-3
    img.lockup.d-none.d-sm-block(:src="productLockup" alt="ISCC generator")
    img.logo.d-sm-none(:src="isccLogo" alt="ISCC")
    .d-flex.align-items-center.gap-4
      a.quiet-link.d-none.d-md-inline(
        href="https://iscc.codes"
        target="_blank"
        rel="noopener"
      ) What is an ISCC?
      a.docs-btn.iscc-btn.iscc-btn--secondary.iscc-btn--thin.iscc-btn--compact(href="/docs" target="_blank")
        UiIcon(name="code" :size="14")
        span API Docs
</template>

<style scoped lang="scss">
.app-header {
  background-color: var(--iscc-deep-navy);

  // Both SVGs carry the logo's clear space in their viewBox. The lockup's viewBox also reaches
  // below the baseline for the g of "generator." (19.2 % of its height); a negative bottom margin
  // of that depth leaves it out of the layout, so the header centers the ISCC logo itself.
  .lockup {
    --lockup-height: 3rem;
    height: var(--lockup-height);
    margin-bottom: calc(var(--lockup-height) * -0.192);
    width: auto;
    display: block;
  }

  .logo {
    height: 2.5rem;
    width: auto;
    display: block;
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
