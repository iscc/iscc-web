<script setup lang="ts">
// One selectable ISCC-UNIT field on the readout strip: unit name, unit code and the
// contiguous bit strip. Also renders the queued/hashing loading states. Styled like the
// unit cards of the first-visit panel (EducationStrip.vue) that it takes over from.
import { computed } from "vue";
import { BIT_ZERO as ZERO, UNIT_STYLE, type UnitKind, seedBits } from "../lib/iscc";

const props = withDefaults(
  defineProps<{
    kind: UnitKind;
    code: string;
    bits: string | null;
    selected: boolean;
    state?: "ready" | "queued" | "hashing";
  }>(),
  { state: "ready" },
);

const emit = defineEmits<{ (e: "select"): void }>();

const style = computed(() => UNIT_STYLE[props.kind]);

const QUEUED = "rgba(18, 54, 99, 0.05)";

const bitCells = computed<Array<{ color: string; anim: boolean }>>(() => {
  if (props.state === "queued") {
    return Array.from({ length: 64 }, () => ({ color: QUEUED, anim: false }));
  }
  if (props.state === "hashing") {
    return Array.from(seedBits(`noise-${props.kind}`), (b) => ({
      color: b === "1" ? style.value.color : ZERO,
      anim: true,
    }));
  }
  if (!props.bits) return [];
  return Array.from(props.bits, (b) => ({ color: b === "1" ? style.value.color : ZERO, anim: false }));
});

const tag = computed(() => {
  if (props.state === "queued") return "queued";
  if (props.state === "hashing") return "hashing…";
  const length = props.bits?.length ?? 0;
  if (!length) return "unit";
  return props.selected ? `${length} bit · selected` : `${length} bit`;
});

// Deterministic per-bit flicker timing so the hashing texture trembles without Math.random.
const bitStyle = (cell: { color: string; anim: boolean }, index: number) => ({
  background: cell.color,
  ...(cell.anim
    ? {
        animation: `bit-flick ${(0.35 + ((index * 53) % 50) / 100).toFixed(2)}s steps(2, end) ${(
          -((index * 37) % 80) / 100
        ).toFixed(2)}s infinite`,
      }
    : {}),
});
</script>

<template lang="pug">
button.unit-field(
  type="button"
  :class="{ selected, ready: state === 'ready' }"
  :disabled="state !== 'ready'"
  :aria-pressed="selected"
  @click="emit('select')"
)
  .uf-color(:style="{ background: style.color }")
  .uf-head(:style="{ background: style.tint }")
    span.uf-name(v-text="style.label")
    span.uf-tag(:class="state" v-text="tag")
  .uf-body
    .uf-code(v-text="code")
    .uf-bits(v-if="bitCells.length")
      .bit(
        v-for="(cell, index) in bitCells"
        :key="index"
        :style="bitStyle(cell, index)"
      )
    .uf-meaning(v-text="style.meaning")
</template>

<style scoped lang="scss">
.unit-field {
  display: block;
  width: 100%;
  padding: 0;
  text-align: left;
  background: #ffffff;
  border: 1px solid #e9ecef;
  cursor: default;
  transition:
    box-shadow 0.15s ease,
    transform 0.15s ease;

  &.ready {
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 16px -8px rgba(18, 54, 99, 0.3);
    }
  }

  &.selected {
    box-shadow:
      0 0 0 3px var(--iscc-coral-red),
      0 8px 18px -6px rgba(18, 54, 99, 0.3);
  }
}

.uf-color {
  height: 6px;
}

.uf-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
}

.uf-name {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--iscc-deep-navy);
}

.uf-tag {
  font-family: var(--bs-font-monospace);
  font-size: 0.62rem;
  color: rgba(18, 54, 99, 0.65);
  white-space: nowrap;

  &.hashing {
    color: #7a5c00;
  }
}

.uf-body {
  padding: 0.55rem 0.75rem 0.65rem;
}

.uf-code {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  color: #495057;
  letter-spacing: 0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.uf-bits {
  display: flex;
  gap: 1px;
  margin-top: 0.45rem;

  .bit {
    width: 100%;
    max-width: 6px;
    height: 18px;
    border-radius: 1px;
    flex-shrink: 1;
  }
}

.uf-meaning {
  font-size: 0.66rem;
  font-weight: 300;
  color: var(--iscc-muted);
  margin-top: 0.5rem;
}
</style>
