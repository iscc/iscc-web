<script setup lang="ts">
// First-visit empty state: teaches the five-layer decomposition in the exact
// silhouette of the live readout that replaces it once a result lands. The code
// slot stays empty; coral appears only for a real code.
import { UNIT_STYLE, type UnitKind } from "../lib/iscc";
import CodeBar from "./CodeBar.vue";
import UiIcon from "./UiIcon.vue";

const CARDS: Array<{ kind: UnitKind; name: string; code: string; compares: string; from: string }> = [
  {
    kind: "meta",
    name: "Meta-Code",
    code: "META-NONE-V0",
    compares: "Metadata similarity",
    from: "From embedded title & description",
  },
  {
    kind: "semantic",
    name: "Semantic-Code",
    code: "SEMANTIC-V0",
    compares: "Semantic similarity",
    from: "From ML embeddings of meaning — experimental",
  },
  {
    kind: "content",
    name: "Content-Code",
    code: "CONTENT-IMAGE-V0",
    compares: "Syntactic similarity",
    from: "From perceptual features per media type",
  },
  {
    kind: "data",
    name: "Data-Code",
    code: "DATA-NONE-V0",
    compares: "Data similarity",
    from: "From the raw bitstream",
  },
  {
    kind: "instance",
    name: "Instance-Code",
    code: "INSTANCE-V0",
    compares: "Exact match",
    from: "Cryptographic checksum — data integrity",
  },
];
</script>

<template lang="pug">
section.education-strip
  .edu-head
    h2.edu-title Inside an ISCC-CODE
    span.edu-sub Each unit is a similarity fingerprint of a different layer of your content.
  CodeBar(:code="null" idle)
  .edu-arrow
    UiIcon(name="arrow-down" :size="18")
  .edu-grid
    .edu-card(v-for="card in CARDS" :key="card.kind")
      .edu-color(:style="{ background: UNIT_STYLE[card.kind].color }")
      .edu-card-head(:style="{ background: UNIT_STYLE[card.kind].tint }")
        .edu-name(v-text="card.name")
        .edu-code(v-text="card.code")
      .edu-card-body
        .edu-compares(v-text="card.compares")
        .edu-from(v-text="card.from")
  .edu-axis
    span Abstract &amp; persistent
    .axis-line
    span Concrete &amp; volatile
  .api-pointer
    .d-flex.align-items-center.gap-3
      .api-icon
        UiIcon(name="code" :size="18")
      div
        .api-head Everything on this page is one REST call away
        .api-calls POST /api/v1/iscc · GET /api/v1/explain/{iscc} · POST /api/v1/simprint
    a.api-btn.iscc-btn.iscc-btn--primary(href="/docs" target="_blank") Open API docs
</template>

<style scoped lang="scss">
.education-strip {
  background: #ffffff;
  border-radius: var(--iscc-radius);
  padding: 2.2rem 2.2rem 2.4rem;
  box-shadow: 0 20px 40px -8px rgba(18, 54, 99, 0.18);

  // Phones: room for the sample code bar's two-line minimum.
  @media (max-width: 575.98px) {
    padding-inline: 1rem;
  }
}

.edu-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.3rem;
  flex-wrap: wrap;
}

.edu-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--iscc-deep-navy);
}

.edu-sub {
  font-size: 0.82rem;
  font-weight: 300;
  color: #6c757d;
}

.edu-arrow {
  display: flex;
  justify-content: center;
  margin: 0.25rem 0;
  color: #adb5bd;
}

.edu-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;

  @media (max-width: 991.98px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 575.98px) {
    grid-template-columns: 1fr;
  }
}

.edu-card {
  overflow: hidden;
  border: 1px solid #e9ecef;
  background: #ffffff;
}

.edu-color {
  height: 6px;
}

.edu-card-head {
  padding: 0.55rem 0.75rem;
}

.edu-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--iscc-deep-navy);
}

.edu-code {
  font-family: var(--bs-font-monospace);
  font-size: 0.62rem;
  color: rgba(18, 54, 99, 0.65);
  margin-top: 0.1rem;
  letter-spacing: -0.01em;
}

.edu-card-body {
  padding: 0.6rem 0.75rem;
}

.edu-compares {
  font-size: 0.74rem;
  font-weight: 500;
  color: #343a40;
}

.edu-from {
  font-size: 0.71rem;
  font-weight: 300;
  color: #6c757d;
  margin-top: 0.2rem;
  line-height: 1.45;
}

.edu-axis {
  margin-top: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;

  span {
    font-size: 0.69rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    color: #6c757d;
    text-transform: uppercase;
  }

  .axis-line {
    flex: 1;
    height: 4px;
    border-radius: 2px;
    background: var(--iscc-bright-yellow);
  }
}

.api-pointer {
  margin-top: 1.75rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: var(--iscc-radius-sm);
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
  background: rgba(0, 84, 178, 0.08);
  color: var(--iscc-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.api-head {
  font-size: 0.88rem;
  font-weight: 600;
  color: #212529;
}

.api-calls {
  font-family: var(--bs-font-monospace);
  font-size: 0.72rem;
  font-weight: 300;
  color: #6c757d;
  margin-top: 0.2rem;
}
</style>
