<script setup lang="ts">
// Navy developer exit below the first-visit panel and the result feed: the main REST calls and a
// link to the API reference at /docs.
import UiIcon from "./UiIcon.vue";
</script>

<template lang="pug">
.api-pointer.on-dark
  .d-flex.align-items-center.gap-3
    .api-icon
      UiIcon(name="code" :size="18")
    div
      .api-head Generate #[span.text-nowrap ISO 24138:2024] ISCCs through the REST API
      .api-calls POST /api/v1/iscc · GET /api/v1/explain/{iscc} · POST /api/v1/simprint
  a.api-btn.iscc-btn.iscc-btn--secondary.iscc-btn--thin.iscc-btn--compact(href="/docs" target="_blank")
    span Open API docs
    UiIcon(name="arrow-right" :size="14")
</template>

<style scoped lang="scss">
// Deep Navy like the header and footer, so the developer exit reads apart from the panels above.
// Spaced from them like result cards from each other.
.api-pointer {
  margin-top: 1.5rem;
  background: var(--iscc-deep-navy);
  border-radius: var(--iscc-radius);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.api-icon {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: var(--iscc-radius-sm);
  background: rgba(255, 255, 255, 0.1);
  color: var(--iscc-light-cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.api-head {
  font-size: 0.88rem;
  font-weight: 600;
  color: #ffffff;
  text-wrap: balance;
}

.api-calls {
  font-family: var(--bs-font-monospace);
  font-size: 0.72rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.2rem;
}
</style>
