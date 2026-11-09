<script setup lang="ts">
// The ISCC-CODE bar. Until a code exists it is an empty slot with the brand's coral dot in it: resting
// with an occasional hop (`idle`, the home page) or hopping busily (while a code is generated). When a
// code arrives, the dot lands, floods the slot with coral, and the characters spin and lock into place
// from left to right. A bar mounted with a known code shows it straight away, as does every bar for
// viewers who prefer reduced motion.
import { nextTick, onUnmounted, ref, watch } from "vue";
import { scramble } from "../lib/iscc";

const props = defineProps<{ code: string | null; idle?: boolean }>();

const HOP_MS = 560; // one dot-hop cycle, floor contact to floor contact (keyframes in main.scss)
const FLOOD_MS = 460; // coral spreading from the dot to the whole bar
const LOCK_START_MS = 240; // the first character locks while the flood is still spreading
const LOCK_STEP_MS = 11; // stagger between characters
const LOCK_POP_MS = 340; // glyph-lock keyframes below
const SPIN_MS = 50; // how long a spinning glyph shows each character

const reducedMotion =
  typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const bar = ref<HTMLElement | null>(null);
const dot = ref<HTMLElement | null>(null);
const shown = ref<string | null>(props.code); // null while the bar is an empty slot
const glyphs = ref<string[] | null>(null); // per-character display while revealing
const locked = ref(0);
let landTimer: ReturnType<typeof setTimeout> | undefined;
let frame = 0;

/** Cancel a pending landing or a running reveal. */
const stop = () => {
  clearTimeout(landTimer);
  cancelAnimationFrame(frame);
  glyphs.value = null;
};

/** Milliseconds until the hopping dot next touches the floor. */
const untilContact = () => {
  const elapsed = Number(dot.value?.getAnimations()[0]?.currentTime ?? 0);
  return HOP_MS - (elapsed % HOP_MS);
};

/** Squash-and-stretch rebound of the bar as the coral lands. */
const BAR_BOUNCE: Keyframe[] = [
  { transform: "scale(1, 1)" },
  { transform: "scale(1.012, 0.86)", offset: 0.18 },
  { transform: "scale(0.996, 1.06)", offset: 0.46 },
  { transform: "scale(1.002, 0.98)", offset: 0.72 },
  { transform: "scale(1, 1)" },
];

/** Flood the bar from the dot's position, then spin the characters and lock them left to right. */
const reveal = async (code: string) => {
  const el = bar.value!;
  const b = el.getBoundingClientRect();
  const d = dot.value!.getBoundingClientRect();
  const x = d.left + d.width / 2 - b.left;
  const y = d.top + d.height / 2 - b.top;
  glyphs.value = Array.from(scramble(code.length, 0));
  locked.value = 0;
  shown.value = code;
  await nextTick();
  const height = el.offsetHeight;
  const radius = Math.hypot(Math.max(x, el.offsetWidth - x), Math.max(y, height - y));
  const from = Math.max(d.width, d.height) / 2;
  el.animate(
    { clipPath: [`circle(${from}px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
    { duration: FLOOD_MS, easing: "cubic-bezier(0.55, 0, 0.25, 1)" },
  );
  // A code that wraps onto two lines grows the bar beyond the one-line slot; ease that growth in.
  if (height !== Math.round(b.height)) {
    el.animate(
      { height: [`${b.height}px`, `${height}px`], overflow: ["hidden", "hidden"] },
      { duration: FLOOD_MS, easing: "cubic-bezier(0.3, 1.3, 0.5, 1)" },
    );
  }
  el.animate(BAR_BOUNCE, { duration: 640, delay: 300, easing: "ease-in-out" });
  const start = performance.now();
  const end = LOCK_START_MS + code.length * LOCK_STEP_MS + LOCK_POP_MS;
  const tick = (now: number) => {
    const t = now - start;
    const count = Math.min(code.length, Math.max(0, Math.floor((t - LOCK_START_MS) / LOCK_STEP_MS) + 1));
    const noise = scramble(code.length, Math.floor(t / SPIN_MS) + 1);
    glyphs.value = Array.from(code, (char, i) => (i < count ? char : noise[i]));
    locked.value = count;
    if (t < end) frame = requestAnimationFrame(tick);
    else glyphs.value = null;
  };
  frame = requestAnimationFrame(tick);
};

watch(
  () => props.code,
  (code) => {
    stop();
    if (!code) {
      shown.value = null;
      return;
    }
    const canReveal =
      !reducedMotion &&
      shown.value === null &&
      typeof bar.value?.animate === "function" &&
      typeof dot.value?.getAnimations === "function";
    if (!canReveal) {
      shown.value = code;
      return;
    }
    landTimer = setTimeout(() => reveal(code), untilContact());
  },
);

onUnmounted(stop);
</script>

<template lang="pug">
.code-bar(ref="bar" :class="shown ? 'iscc-code-bar grain' : { slot: true, idle }")
  template(v-if="!shown")
    .iscc-dot(ref="dot")
    span.slot-label Your ISCC-CODE will land here
  //- One span per character, also when settled: an odd-length code splits evenly in two ways, and
  //- plain text and spans break that tie differently, so the code would jump when the reveal ends.
  span(v-else :aria-hidden="glyphs ? 'true' : undefined")
    span.glyph(
      v-for="(glyph, i) in glyphs ?? shown"
      :key="i"
      :class="glyphs ? (i < locked ? 'locked' : 'spinning') : undefined"
      :style="glyphs && i >= locked ? { animationDelay: `${-(i % 5) * 17}ms` } : undefined"
      v-text="glyph"
    )
  span.visually-hidden(v-if="glyphs" v-text="shown")
</template>

<style scoped lang="scss">
.code-bar {
  transform-origin: 50% 100%;
}

// The empty slot: same footprint as a one-line bar, with the dot resting at the start of the line where
// the code will begin.
.slot {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 48px;
  padding-left: calc(1rem + 14px + 0.75rem);
  border: 1.5px dashed #ced4da;
  border-radius: var(--iscc-radius-sm);

  .iscc-dot {
    position: absolute;
    left: 1rem;
    top: calc(50% - 7px);
    animation: dot-hop 560ms infinite;
  }

  &.idle .iscc-dot {
    animation: dot-idle 4s 1s infinite;
  }
}

.slot-label {
  font-family: var(--bs-font-monospace);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  color: var(--iscc-muted);
  text-wrap: balance; // the narrowest phones split it into two even lines
}

// Spinning glyphs shimmer on a short vertical reel; each one drops into place with a flash as it locks.
// Glyphs stay inline and move by relative offset (not transform), so the code wraps exactly like the
// plain text that replaces it.
.glyph {
  position: relative;

  &.spinning {
    opacity: 0.55;
    animation: reel 80ms linear infinite alternate;
  }

  &.locked {
    animation: glyph-lock 340ms cubic-bezier(0.3, 1.5, 0.5, 1) both;
  }
}

@keyframes reel {
  from {
    top: -0.12em;
  }

  to {
    top: 0.12em;
  }
}

@keyframes glyph-lock {
  from {
    top: -0.55em;
    opacity: 0.5;
    text-shadow: 0 0 0.45em #ffffff;
  }

  to {
    top: 0;
    opacity: 1;
    text-shadow: none;
  }
}
</style>
