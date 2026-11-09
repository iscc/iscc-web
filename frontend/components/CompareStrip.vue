<script setup lang="ts">
// Diff readout for two docked specimens: aligned A/B bit strips per layer,
// Hamming match percentages and a plain-language verdict ribbon. Light like the single
// readout it replaces, with diff cards built like its ISCC-UNIT fields (UnitField.vue).
import { computed, ref } from "vue";
import { BIT_ZERO, UNIT_STYLE, compareUnits, pctColor, verdict } from "../lib/iscc";
import UiIcon from "./UiIcon.vue";

const props = defineProps<{ a: IsccWeb.Specimen; b: IsccWeb.Specimen }>();

const diffs = computed(() => compareUnits(props.a.explain?.units ?? [], props.b.explain?.units ?? []));
const verdictInfo = computed(() => verdict(diffs.value));

const EQUAL_A = "#a6db50";
const EQUAL_B = "#85b53a";
const DIFF_A = "#f56169";
const DIFF_B = "#c94850";

const rows = computed(() =>
  diffs.value.map((diff) => {
    const comparable = diff.pct !== null && diff.a !== null && diff.b !== null;
    const { color: unitColor, tint, label } = UNIT_STYLE[diff.kind];
    const plain = (bits: string | undefined) =>
      bits ? Array.from(bits, (b) => (b === "1" ? unitColor : BIT_ZERO)) : [];
    let cellsA: string[];
    let cellsB: string[];
    if (comparable) {
      const aBits = diff.a!.hash_bits;
      const bBits = diff.b!.hash_bits;
      cellsA = [];
      cellsB = [];
      for (let i = 0; i < aBits.length; i++) {
        const equal = aBits[i] === bBits[i];
        cellsA.push(equal ? EQUAL_A : DIFF_A);
        cellsB.push(equal ? EQUAL_B : DIFF_B);
      }
    } else {
      cellsA = plain(diff.a?.hash_bits);
      cellsB = plain(diff.b?.hash_bits);
    }
    return {
      kind: diff.kind,
      label,
      color: unitColor,
      tint,
      note: diff.note,
      pct: diff.pct,
      pctText: diff.pct !== null ? `${diff.pct}%` : "—",
      tone: diff.pct !== null ? pctColor(diff.pct) : null,
      cellsA,
      cellsB,
    };
  }),
);

const isccOf = (s: IsccWeb.Specimen) => s.metadata?.iscc ?? s.explain?.iscc ?? "";

const report = computed(() =>
  [
    "ISCC comparison",
    `A: ${props.a.label} — ${isccOf(props.a)}`,
    `B: ${props.b.label} — ${isccOf(props.b)}`,
    ...rows.value.map((row) => `${row.label}: ${row.pctText} — ${row.note}`),
    `Verdict: ${verdictInfo.value.headline} ${verdictInfo.value.detail}`,
  ].join("\n"),
);

const copied = ref(false);
const copyReport = async () => {
  try {
    await navigator.clipboard?.writeText(report.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1600);
  } catch {
    // clipboard unavailable - ignore
  }
};
</script>

<template lang="pug">
.compare-strip
  .strip-label
    span ISCC-UNITS · DIFF · TOP STRIP = A · BOTTOM STRIP = B
    .rule
  .diff-grid(:style="{ '--cols': rows.length }")
    .diff-card(v-for="row in rows" :key="row.kind")
      .dc-color(:style="{ background: row.color }")
      .dc-head(:style="{ background: row.tint }")
        span.dc-name(v-text="row.label")
        span.dc-pct(:style="row.tone ? { color: row.tone.text } : undefined" v-text="row.pctText")
      .dc-body
        .dc-bits
          .bit(
            v-for="(color, index) in row.cellsA"
            :key="index"
            :style="{ background: color }"
          )
        .dc-bits.b-row
          .bit(
            v-for="(color, index) in row.cellsB"
            :key="index"
            :style="{ background: color }"
          )
        .dc-bar
          .dc-bar-fill(v-if="row.tone" :style="{ width: `${row.pct}%`, background: row.tone.fill }")
        .dc-note(v-text="row.note")
  .verdict-ribbon
    .verdict-text
      UiIcon(
        name="check-circle"
        :size="20"
        :stroke-width="2.2"
      )
      div
        span.verdict-head(v-text="verdictInfo.headline")
        span.verdict-detail(v-text="' ' + verdictInfo.detail")
    button.copy-report(type="button" @click="copyReport")
      span(v-text="copied ? 'Copied!' : 'Copy report'")
</template>

<style scoped lang="scss">
.compare-strip {
  border-top: 1px solid #e9ecef;
  padding: 1.25rem 1.75rem 1.5rem;

  @media (max-width: 575.98px) {
    padding-inline: 1rem;
  }
}

.strip-label {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.5rem;

  span {
    font-family: var(--bs-font-monospace);
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    color: var(--iscc-muted);
  }

  .rule {
    flex: 1;
    height: 1px;
    background: #e9ecef;
  }
}

.diff-grid {
  display: grid;
  grid-template-columns: repeat(var(--cols, 4), 1fr);
  gap: 0.65rem;

  @media (max-width: 991.98px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 575.98px) {
    grid-template-columns: 1fr;
  }
}

.diff-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
}

.dc-color {
  height: 6px;
}

.dc-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
}

.dc-name {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--iscc-deep-navy);
}

.dc-pct {
  font-family: var(--bs-font-monospace);
  font-size: 0.88rem;
  font-weight: 700;
  color: rgba(18, 54, 99, 0.65);
}

.dc-body {
  padding: 0.6rem 0.75rem 0.7rem;
}

.dc-bits {
  display: flex;
  gap: 1px;

  &.b-row {
    margin-top: 2px;
  }

  .bit {
    width: 100%;
    max-width: 6px;
    height: 12px;
    border-radius: 1px;
    flex-shrink: 1;
  }
}

.dc-bar {
  margin-top: 0.6rem;
  height: 5px;
  border-radius: 3px;
  background: rgba(18, 54, 99, 0.08);
  overflow: hidden;
}

.dc-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.dc-note {
  font-size: 0.66rem;
  font-weight: 300;
  color: var(--iscc-muted);
  margin-top: 0.5rem;
}

.verdict-ribbon {
  margin-top: 1rem;
  background: var(--iscc-bright-yellow);
  border-radius: var(--iscc-radius-sm);
  padding: 0.8rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.verdict-text {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--iscc-deep-navy);
}

.verdict-head {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--iscc-deep-navy);
}

.verdict-detail {
  font-size: 0.81rem;
  font-weight: 400;
  color: rgba(18, 54, 99, 0.8);
}

.copy-report {
  background: none;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--iscc-deep-navy);
  cursor: pointer;
  flex-shrink: 0;
  text-decoration: underline;
  text-underline-offset: 3px;
  padding: 0;
}
</style>
