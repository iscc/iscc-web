<script setup lang="ts">
// Heading line above a row of ISCC-UNIT cards that doubles as their axis: from the abstract,
// persistent layers (left) to the concrete, volatile ones (right). The first-visit panel and the
// result readout share it, so the heading stays put when one replaces the other.
</script>

<template lang="pug">
.units-axis
  span.axis-end ABSTRACT&nbsp;&amp; PERSISTENT
  .rule.to-start
  span.axis-title ISCC-UNITS
  .rule.to-end
  span.axis-end CONCRETE&nbsp;&amp; VOLATILE
</template>

<style scoped lang="scss">
// On phones the end labels wrap onto two lines so the title and both rules keep fitting.
.units-axis {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.5rem;

  span {
    font-family: var(--bs-font-monospace);
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    color: var(--iscc-muted);
  }

  .axis-end:last-child {
    text-align: right;
  }

  .axis-title {
    flex-shrink: 0;
    font-weight: 700;
    color: var(--iscc-deep-navy);
    white-space: nowrap;
  }

  .rule {
    position: relative;
    flex: 1 1 1rem;
    min-width: 1rem;
    height: 1px;
    color: #adb5bd;
    background: currentColor;

    // Open arrowhead at the outer end, pointing at the end label.
    &::before {
      content: "";
      position: absolute;
      top: 50%;
      width: 6px;
      height: 6px;
      border: solid currentColor;
      border-width: 0 0 1px 1px;
    }

    &.to-start::before {
      left: 1px;
      transform: translateY(-50%) rotate(45deg);
    }

    &.to-end::before {
      right: 1px;
      transform: translateY(-50%) rotate(-135deg);
    }
  }

  @media (max-width: 575.98px) {
    gap: 0.4rem;

    .rule {
      min-width: 0.5rem;
    }
  }
}
</style>
