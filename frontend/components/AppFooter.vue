<script setup lang="ts">
// Navy footer mirroring the header: copyright, legal pages and developer exits. The name is
// established in the header, so the footer carries the brand symbol only.
import isccSymbol from "../assets/iscc-icon-white-coral.svg";
import UiIcon from "./UiIcon.vue";
</script>

<template lang="pug">
footer.app-footer.grain.on-dark
  .container-xl.d-flex.align-items-center.justify-content-between.gap-4.flex-wrap.py-2
    .d-flex.align-items-center.gap-2
      img.logo(:src="isccSymbol" alt="ISCC")
      span.copyright Copyright © 2022–2026 ISCC Foundation
    .d-flex.align-items-center.gap-4.flex-wrap
      a.legal(
        href="https://iscc.foundation/privacy/"
        target="_blank"
        rel="noopener"
      ) Privacy Policy
      a.legal(
        href="https://iscc.foundation/cookies"
        target="_blank"
        rel="noopener"
      ) Cookie Policy
      a.legal(
        href="https://iscc.foundation/imprint"
        target="_blank"
        rel="noopener"
      ) Imprint
      a.legal(
        href="https://iscc.foundation/disclaimer"
        target="_blank"
        rel="noopener"
      ) Disclaimer
      .divider
      a.exit(href="/docs" target="_blank")
        UiIcon(name="code" :size="13")
        span API Docs
      a.exit(
        href="https://github.com/iscc/iscc-web"
        target="_blank"
        rel="noopener"
      )
        UiIcon(
          name="github"
          :size="13"
          :stroke-width="1.8"
        )
        span Source Code
</template>

<style scoped lang="scss">
.app-footer {
  background-color: var(--iscc-deep-navy);
  margin-top: auto;

  // The SVG symbol carries its clear space in the viewBox (brand screen minimum: 32 px wide).
  .logo {
    height: 2.25rem;
    width: auto;
    display: block;
  }

  .copyright {
    color: rgba(255, 255, 255, 0.55);
    font-size: 0.8rem;
    font-weight: 300;
  }

  .legal {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.8rem;
    font-weight: 300;
    text-decoration: none;

    &:hover {
      color: #ffffff;
    }
  }

  .divider {
    width: 1px;
    height: 0.9rem;
    background: rgba(255, 255, 255, 0.25);
  }

  .exit {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.8rem;
    font-weight: 500;
    text-decoration: none;

    &:hover {
      color: #ffffff;
    }
  }
}
</style>
