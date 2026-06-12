<script setup lang="ts">
// Inline stroke icon (24×24 viewBox) from the static set in lib/icons.ts.
import { ICONS, type IconName } from "../lib/icons";

withDefaults(defineProps<{ name: IconName; size?: number; strokeWidth?: number }>(), {
  size: 16,
  strokeWidth: 2,
});
</script>

<template lang="pug">
svg.ui-icon(
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
  :stroke-width="strokeWidth"
  :width="size"
  :height="size"
  v-html="ICONS[name]"
)
</template>

<style scoped lang="scss">
.ui-icon {
  flex-shrink: 0;
  display: inline-block;
  vertical-align: -0.125em;
}
</style>
