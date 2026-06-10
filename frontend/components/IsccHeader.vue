<script setup lang="ts">
import isccLogo from "../assets/iscc-logo-extended-black.svg?raw";
</script>

<template lang="pug">
header
  .header-bar
    .container
      .d-flex.align-items-center.justify-content-between.py-3
        .logo(v-html="isccLogo")
        span.tagline.d-none.d-md-block The DNA of your digital content
  .hero
    .container.py-4
      h1.hero-title ISCC #[span.accent Generator]
      p.hero-subtitle.mb-0 Generate International Standard Content Codes (ISO 24138) for your media files.
</template>

<style scoped lang="scss">
.header-bar {
  background-color: var(--iscc-deep-navy);

  .logo :deep(svg) {
    height: 2.5rem;
    width: auto;
    filter: invert(1);
  }

  .tagline {
    color: var(--iscc-light-cyan);
    font-weight: 300;
  }
}

.hero {
  background-color: var(--iscc-blue);
  color: #ffffff;

  .hero-title {
    font-weight: 600;

    .accent {
      color: var(--iscc-bright-yellow);
    }
  }

  .hero-subtitle {
    color: #f8f9fa;
    font-weight: 300;
  }
}
</style>
