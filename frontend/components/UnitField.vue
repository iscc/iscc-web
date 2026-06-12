<script setup lang="ts">
// One selectable ISCC-UNIT field on the navy readout strip: swatch, unit code
// and the contiguous bit strip. Also renders the queued/hashing loading states.
import { computed } from "vue";
import { UNIT_STYLE, type UnitKind, seedBits } from "../lib/iscc";

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

const ZERO = "rgba(255, 255, 255, 0.25)";
const QUEUED = "rgba(255, 255, 255, 0.08)";

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
  .uf-head
    .uf-name
      .swatch(:style="{ background: style.color }")
      span(v-text="style.label")
    span.uf-tag(:class="state" v-text="tag")
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
  text-align: left;
  background: rgba(255, 255, 255, 0.07);
  border: 2px solid rgba(255, 255, 255, 0.16);
  border-radius: 0.65rem;
  padding: 0.8rem 0.9rem 0.85rem;
  cursor: default;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    transform 0.15s ease;

  &.ready {
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
    }
  }

  &.selected {
    border-color: var(--iscc-bright-yellow);
    box-shadow:
      0 0 0 3px rgba(255, 195, 0, 0.3),
      0 8px 20px rgba(0, 0, 0, 0.35);
  }
}

.uf-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.uf-name {
  display: flex;
  align-items: center;
  gap: 0.45rem;

  .swatch {
    width: 10px;
    height: 10px;
    border-radius: 3px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    flex-shrink: 0;
  }

  span {
    font-family: var(--bs-font-monospace);
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #ffffff;
  }
}

.uf-tag {
  font-family: var(--bs-font-monospace);
  font-size: 0.62rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;

  &.hashing {
    color: var(--iscc-bright-yellow);
  }
}

.uf-code {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 0.4rem;
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
  color: rgba(255, 255, 255, 0.65);
  margin-top: 0.5rem;
}
</style>
