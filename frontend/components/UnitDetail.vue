<script setup lang="ts">
// Detail panel for the selected ISCC-UNIT layer: explanation, type/hex chips,
// specimen preview (or code structure) and the per-layer experiment.
import { computed, ref, watch } from "vue";
import { UNIT_STYLE, type UnitKind, formatBytes, unitTypeLabel } from "../lib/iscc";
import { unitCopy } from "../lib/unit-copy";
import { apiService } from "../services/api.service";
import UiIcon from "./UiIcon.vue";

const props = defineProps<{
  specimen: IsccWeb.Specimen;
  kind: UnitKind;
  unit: Api.IsccUnit | null;
}>();

const emit = defineEmits<{ (e: "embed", formData: IsccWeb.MetadataFormData): void }>();

const style = computed(() => UNIT_STYLE[props.kind]);
const copy = computed(() => unitCopy(props.kind, props.specimen.metadata?.mode));
const pillText = computed(
  () => `${style.value.label} LAYER SELECTED${props.kind === "semantic" ? " · EXPERIMENTAL" : ""}`,
);

const simprintCount = computed(() => {
  const features = props.specimen.metadata?.features ?? [];
  return features.find((f) => f.maintype === props.kind)?.simprints.length ?? 0;
});

const mediaId = computed(() => props.specimen.metadata?.media_id ?? null);
const canEmbed = computed(() => props.kind === "meta" && props.specimen.kind === "file" && !!mediaId.value);
const downloadUrl = computed(() => (mediaId.value ? apiService.downloadUrl(mediaId.value) : ""));

const form = ref<IsccWeb.MetadataFormData>({
  name: props.specimen.metadata?.name ?? "",
  description: props.specimen.metadata?.description ?? "",
});
watch(
  () => props.specimen.metadata,
  (metadata) => {
    form.value.name = metadata?.name ?? "";
    form.value.description = metadata?.description ?? "";
  },
);

const thumbSrc = computed(() => props.specimen.previewUrl ?? props.specimen.metadata?.thumbnail ?? null);

const previewFacts = computed(() => {
  const m = props.specimen.metadata;
  if (!m) return "";
  const parts = [m.mediatype];
  if (m.filesize) parts.push(formatBytes(m.filesize));
  if (m.width && m.height) parts.push(`${m.width}×${m.height}`);
  if (m.characters) parts.push(`${m.characters.toLocaleString()} characters`);
  if (m.language) parts.push(m.language);
  return parts.filter(Boolean).join(" · ");
});
</script>

<template lang="pug">
.unit-detail(:style="{ borderTopColor: style.color }")
  .layer-pill
    span.pill-swatch(:style="{ background: style.color }")
    span(v-text="pillText")
  .detail-grid(:class="{ 'code-mode': specimen.kind === 'code' }")
    .explain-col
      h3.layer-title(:style="{ color: style.accent }" v-text="copy.title")
      p.layer-body(v-text="copy.body")
      .chips
        span.chip.experimental(v-if="kind === 'semantic'") EXPERIMENTAL · NON-ISO
        span.chip.mono(v-if="unit" v-text="unitTypeLabel(unit.readable)")
        span.chip.mono(v-if="unit" v-text="`hex 0x${unit.hash_hex}`")
        span.chip.mono(v-if="simprintCount" v-text="`${simprintCount} granular simprints`")
    .panel(v-if="specimen.kind !== 'code'")
      .panel-label Specimen preview
      .preview-row
        img.preview-thumb(
          v-if="thumbSrc"
          :src="thumbSrc"
          alt=""
        )
        .preview-thumb.glyph(v-else)
          UiIcon(name="file" :size="20")
        .preview-facts
          .pf-name(v-text="specimen.label")
          .pf-meta(v-text="previewFacts")
      .privacy-note Private to you · auto-deleted after one hour
    .panel(v-else-if="specimen.explain")
      .panel-label Code structure
      dl.structure
        dt readable
        dd(v-text="specimen.explain.readable")
        dt decomposed
        dd(v-text="specimen.explain.decomposed")
        dt multiformat
        dd(v-text="specimen.explain.multiformat")
    .panel(v-if="specimen.kind !== 'code'")
      .panel-label Experiment with this layer
      template(v-if="canEmbed")
        p.exp-body Add a title and description — they are written into a copy of your file and the ISCC is re-generated. Watch how only the META field moves.
        input.form-control.form-control-sm.mb-2(
          type="text"
          placeholder="Title"
          v-model="form.name"
          :disabled="specimen.embedBusy"
        )
        input.form-control.form-control-sm.mb-2(
          type="text"
          placeholder="Description"
          v-model="form.description"
          :disabled="specimen.embedBusy"
        )
        button.embed-btn(
          type="button"
          :disabled="specimen.embedBusy"
          @click="emit('embed', { ...form })"
        )
          span(v-text="specimen.embedBusy ? 'Embedding…' : 'Embed metadata → re-decode'")
        .embed-error(v-if="specimen.embedError" v-text="specimen.embedError")
        a.updated-link(v-if="specimen.metadataChanged && mediaId" :href="downloadUrl")
          UiIcon(name="download" :size="13")
          span Download updated file
      template(v-else)
        p.exp-body(v-text="copy.tip")
        .exp-hint Then use “Compare with another file” below to see the layers diverge.
</template>

<style scoped lang="scss">
.unit-detail {
  border-top: 4px solid transparent;
  padding: 1.6rem 1.75rem;
  position: relative;
  transition: border-color 0.2s ease;
}

.layer-pill {
  position: absolute;
  top: -0.85rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--iscc-deep-navy);
  color: #ffffff;
  font-family: var(--bs-font-monospace);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  padding: 0.25rem 0.9rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  white-space: nowrap;

  .pill-swatch {
    width: 8px;
    height: 8px;
    border-radius: 2px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    display: inline-block;
  }
}

.detail-grid {
  display: grid;
  grid-template-columns: 1.25fr 1fr 1fr;
  gap: 1.75rem;

  &.code-mode {
    grid-template-columns: 1.25fr 1fr;
  }

  @media (max-width: 991.98px) {
    grid-template-columns: 1fr !important;
    gap: 1rem;
  }
}

.layer-title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.layer-body {
  margin: 0;
  font-size: 0.84rem;
  font-weight: 300;
  line-height: 1.65;
  color: #495057;
}

.chips {
  margin-top: 0.85rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.chip {
  font-size: 0.69rem;
  font-weight: 500;
  background: rgba(18, 54, 99, 0.05);
  border: 1px solid rgba(18, 54, 99, 0.18);
  color: var(--iscc-deep-navy);
  padding: 0.3rem 0.7rem;
  border-radius: 9999px;

  &.mono {
    font-family: var(--bs-font-monospace);
  }

  &.experimental {
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #7a5c00;
    background: rgba(255, 195, 0, 0.25);
    border-color: rgba(255, 195, 0, 0.6);
  }
}

.panel {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.65rem;
  padding: 1rem 1.1rem;
}

.panel-label {
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #6c757d;
  margin-bottom: 0.65rem;
}

.preview-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.preview-thumb {
  width: 4rem;
  height: 4rem;
  border-radius: 0.4rem;
  object-fit: cover;
  flex-shrink: 0;

  &.glyph {
    background: #ffffff;
    border: 1px solid #dee2e6;
    color: var(--iscc-deep-navy);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.pf-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #212529;
  word-break: break-all;
}

.pf-meta {
  font-family: var(--bs-font-monospace);
  font-size: 0.66rem;
  font-weight: 300;
  color: #6c757d;
  margin-top: 0.2rem;
}

.privacy-note {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e9ecef;
  font-size: 0.69rem;
  font-weight: 300;
  color: #adb5bd;
}

.structure {
  margin: 0;

  dt {
    font-family: var(--bs-font-monospace);
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #adb5bd;
  }

  dd {
    font-family: var(--bs-font-monospace);
    font-size: 0.69rem;
    color: #343a40;
    word-break: break-all;
    margin: 0.15rem 0 0.6rem;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.exp-body {
  margin: 0 0 0.65rem;
  font-size: 0.76rem;
  font-weight: 300;
  line-height: 1.55;
  color: #6c757d;
}

.embed-btn {
  display: block;
  width: 100%;
  background: var(--iscc-blue);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 600;
  text-align: center;
  padding: 0.55rem 0;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;

  &:disabled {
    opacity: 0.55;
    cursor: wait;
  }
}

.embed-error {
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: var(--iscc-coral-red);
  word-break: break-all;
}

.updated-link {
  margin-top: 0.6rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--iscc-blue);
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

.exp-hint {
  font-size: 0.69rem;
  font-weight: 300;
  color: #adb5bd;
}
</style>
