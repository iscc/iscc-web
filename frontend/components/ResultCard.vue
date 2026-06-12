<script setup lang="ts">
// Decoder readout card: one specimen's full lifecycle — upload progress, the
// decode animation, the selectable unit-field strip with its per-layer detail
// panel, and the docked comparison mode.
import { computed, onUnmounted, ref, watch } from "vue";
import { type UnitKind, formatBytes, scramble, unitKindFromIscc } from "../lib/iscc";
import { apiService } from "../services/api.service";
import CompareStrip from "./CompareStrip.vue";
import UiIcon from "./UiIcon.vue";
import UnitDetail from "./UnitDetail.vue";
import UnitField from "./UnitField.vue";

const props = defineProps<{
  specimen: IsccWeb.Specimen;
  compareTarget: IsccWeb.Specimen | null;
  compareOptions: Array<{ id: string; label: string; iscc: string }>;
}>();

const emit = defineEmits<{
  (e: "remove"): void;
  (e: "embed", formData: IsccWeb.MetadataFormData): void;
  (e: "compare", targetId: string): void;
  (e: "eject"): void;
  (e: "swap"): void;
}>();

const working = computed(() => props.specimen.status === "uploading" || props.specimen.status === "processing");

// --- decode animation ---------------------------------------------------------

const reducedMotion =
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const tick = ref(0);
let timer: ReturnType<typeof setInterval> | null = null;
watch(
  working,
  (active) => {
    if (active && !reducedMotion && !timer) {
      timer = setInterval(() => {
        tick.value++;
      }, 120);
    }
    if (!active && timer) {
      clearInterval(timer);
      timer = null;
    }
  },
  { immediate: true },
);
onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// --- readout data ---------------------------------------------------------------

interface UnitView {
  kind: UnitKind;
  code: string;
  bits: string | null;
  unit: Api.IsccUnit | null;
}

const unitViews = computed<UnitView[]>(() => {
  const explain = props.specimen.explain;
  if (explain) {
    return explain.units.flatMap((unit) => {
      const kind = unitKindFromIscc(unit.iscc_unit);
      return kind ? [{ kind, code: unit.iscc_unit.replace("ISCC:", ""), bits: unit.hash_bits, unit }] : [];
    });
  }
  return (props.specimen.metadata?.units ?? []).flatMap((u) => {
    const kind = unitKindFromIscc(u);
    return kind ? [{ kind, code: u.replace("ISCC:", ""), bits: null, unit: null }] : [];
  });
});

const pendingKinds = computed<UnitKind[]>(() =>
  props.specimen.semantic
    ? ["meta", "semantic", "content", "data", "instance"]
    : ["meta", "content", "data", "instance"],
);

const selected = ref<UnitKind | null>(null);
watch(
  unitViews,
  (views) => {
    if (!views.length) {
      selected.value = null;
      return;
    }
    if (!views.some((v) => v.kind === selected.value)) {
      selected.value = views.some((v) => v.kind === "content") ? "content" : views[0].kind;
    }
  },
  { immediate: true },
);
const selectedView = computed(() => unitViews.value.find((v) => v.kind === selected.value) ?? null);

const iscc = computed(() => props.specimen.metadata?.iscc ?? props.specimen.explain?.iscc ?? null);
const scrambleLength = computed(() => (props.specimen.semantic ? 68 : 64));
const codeText = computed(() => {
  if (iscc.value && !working.value) return iscc.value;
  if (reducedMotion) return `ISCC:${"·".repeat(scrambleLength.value)}`;
  return `ISCC:${scramble(scrambleLength.value, tick.value)}`;
});
const pendingCode = (index: number) => (reducedMotion ? "·".repeat(16) : scramble(16, tick.value * 31 + index * 7));

const unitsLabel = computed(() => {
  if (working.value) return "ISCC-UNITS · SELF-DESCRIBING · DECODING…";
  const count = unitViews.value.length;
  const note = unitViews.value.some((v) => v.kind === "semantic")
    ? " · SEMANTIC IS EXPERIMENTAL / NON-ISO"
    : " · CLICK A FIELD TO INSPECT ITS LAYER";
  return `ISCC-UNITS · ${count} OF ${count}${note}`;
});

// --- card head -------------------------------------------------------------------

const pill = computed(() => {
  const s = props.specimen;
  switch (s.status) {
    case "uploading":
      return {
        cls: "busy",
        text:
          `UPLOADING · ${s.progress}%` +
          (s.bytesTotal ? ` · ${formatBytes(s.bytesUploaded)} / ${formatBytes(s.bytesTotal)}` : ""),
      };
    case "processing":
      return { cls: "busy", text: s.kind === "code" ? "DECODING CODE…" : "DECODING · GENERATING ISCC-UNITS…" };
    case "done":
      return s.kind === "code" || s.elapsed === null
        ? { cls: "done", text: "DECODED" }
        : { cls: "done", text: `DONE IN ${s.elapsed.toFixed(1)} S` };
    default:
      return { cls: "fail", text: "FAILED" };
  }
});

const headFacts = computed(() => {
  const s = props.specimen;
  if (s.kind === "code") {
    const readable = s.explain?.readable;
    const head = readable ? readable.split("-").slice(0, 4).join("-") : "decoding";
    const count = unitViews.value.length;
    return count ? `${head} · ${count} units` : head;
  }
  const m = s.metadata;
  const parts = [m?.mediatype ?? s.typeHint];
  const size = m?.filesize ?? s.bytesTotal;
  if (size) parts.push(formatBytes(size));
  if (m?.width && m?.height) parts.push(`${m.width}×${m.height}`);
  if (m?.duration) parts.push(`${m.duration} s`);
  if (m?.characters) parts.push(`${m.characters.toLocaleString()} characters`);
  if (m?.language) parts.push(m.language);
  return parts.filter(Boolean).join(" · ");
});

const glyphIcon = computed(() => {
  if (props.specimen.kind === "code") return "search";
  const type = props.specimen.metadata?.mediatype ?? props.specimen.typeHint;
  const mode = props.specimen.metadata?.mode;
  if (mode === "image" || type.startsWith("image/")) return "image";
  if (mode === "audio" || type.startsWith("audio/")) return "music";
  if (mode === "video" || type.startsWith("video/")) return "film";
  if (mode === "text" || type.startsWith("text/")) return "type";
  return "file";
});

const thumbSrc = computed(() => props.specimen.previewUrl ?? props.specimen.metadata?.thumbnail ?? null);

const downloadHref = computed(() => {
  const mediaId = props.specimen.metadata?.media_id;
  return props.specimen.kind !== "code" && props.specimen.status === "done" && mediaId
    ? apiService.downloadUrl(mediaId)
    : null;
});

// While working we only know the toggle; once settled the chip must reflect the
// actual units (embed re-processing drops the semantic unit server-side).
const hasSemanticChip = computed(() => {
  if (props.specimen.kind === "code") return false;
  if (working.value) return props.specimen.semantic;
  return unitViews.value.some((view) => view.kind === "semantic");
});

// --- progress track ---------------------------------------------------------------

const trackStyle = computed(() => {
  const s = props.specimen;
  if (s.status === "uploading") return { width: `${Math.min(s.progress, 100) * 0.7}%` };
  if (s.status === "processing") return { width: "92%", transition: "width 6s ease-out" };
  if (s.status === "done") return { width: "100%", opacity: "0" };
  return { width: "0%" };
});

// --- code copy ---------------------------------------------------------------------

const copied = ref(false);
const copyCode = async () => {
  if (!iscc.value) return;
  try {
    await navigator.clipboard?.writeText(iscc.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1600);
  } catch {
    // clipboard unavailable - ignore
  }
};

// --- raw JSON & compare picker -------------------------------------------------------

const rawOpen = ref(false);
const rawJson = computed(() => JSON.stringify(props.specimen.metadata ?? props.specimen.explain, null, 2));

const pickerOpen = ref(false);
const onCompareClick = () => {
  if (props.compareOptions.length === 1) {
    emit("compare", props.compareOptions[0].id);
    return;
  }
  pickerOpen.value = !pickerOpen.value;
};
const pickCompare = (id: string) => {
  pickerOpen.value = false;
  emit("compare", id);
};

// --- comparison mode ------------------------------------------------------------------

const compareA = computed(() =>
  props.specimen.compareSwapped && props.compareTarget ? props.compareTarget : props.specimen,
);
const compareB = computed(() => (props.specimen.compareSwapped ? props.specimen : props.compareTarget));

const isccOf = (s: IsccWeb.Specimen) => s.metadata?.iscc ?? s.explain?.iscc ?? "";
const shortIscc = (s: IsccWeb.Specimen) => {
  const code = isccOf(s);
  return code.length > 22 ? `${code.slice(0, 21)}…` : code;
};
const sideThumb = (s: IsccWeb.Specimen) => s.previewUrl ?? s.metadata?.thumbnail ?? undefined;
</script>

<template lang="pug">
article.result-card(:class="`is-${specimen.status}`")
  //- ================= comparison mode =================
  template(v-if="compareTarget && compareB")
    .compare-head
      .pair
        .side
          span.side-tag A
          img.thumb-mini(
            v-if="sideThumb(compareA)"
            :src="sideThumb(compareA)"
            alt=""
          )
          .thumb-mini.glyph(v-else)
            UiIcon(name="file" :size="14")
          .who
            .name(v-text="compareA.label")
            .code-mini(v-text="shortIscc(compareA)")
        UiIcon.swap-glyph(name="compare" :size="17")
        .side
          span.side-tag B
          img.thumb-mini(
            v-if="sideThumb(compareB)"
            :src="sideThumb(compareB)"
            alt=""
          )
          .thumb-mini.glyph(v-else)
            UiIcon(name="file" :size="14")
          .who
            .name(v-text="compareB.label")
            .code-mini(v-text="shortIscc(compareB)")
      .actions
        button.ghost-btn(type="button" @click="emit('swap')")
          UiIcon(name="compare" :size="13")
          span Swap
        button.ghost-btn(type="button" @click="emit('eject')")
          UiIcon(name="x" :size="13")
          span Eject B
    CompareStrip(:a="compareA" :b="compareB")
    .compare-legend
      .legend-items
        .legend-item
          .swatch(style="background: #a6db50")
          span bit equal in A and B
        .legend-item
          .swatch(style="background: #f56169")
          span bit different
      span.legend-hint Eject B to return to the single readout — nothing else changes.
  //- ================= single mode =================
  template(v-else)
    .card-head
      .ident
        img.thumb(
          v-if="thumbSrc"
          :src="thumbSrc"
          alt=""
        )
        .thumb.glyph(v-else)
          UiIcon(:name="glyphIcon" :size="18")
        .who
          .name(v-text="specimen.label")
          .facts(v-text="headFacts")
      .head-actions
        span.chip-semantic(v-if="hasSemanticChip") SEMANTIC ON
        .status-pill(:class="pill.cls" role="status")
          .dot
          span(v-text="pill.text")
        a.icon-btn(
          v-if="downloadHref"
          :href="downloadHref"
          title="Download file"
          aria-label="Download file"
        )
          UiIcon(name="download" :size="15")
        button.icon-btn(
          type="button"
          title="Remove"
          aria-label="Remove"
          @click="emit('remove')"
        )
          UiIcon(name="trash" :size="15")
    .alert-strip(v-if="specimen.status === 'error'")
      UiIcon(name="alert" :size="16")
      div
        b Processing failed.
        span(v-text="' ' + (specimen.error ?? 'Unknown error')")
    .navy-strip.grain(v-else)
      .progress-track(:style="trackStyle")
      .scan-line(v-if="specimen.status === 'processing' && !reducedMotion")
      .code-row
        .code-bar.grain(:class="{ working }")
          span(v-text="codeText")
        button.copy-btn(
          type="button"
          :disabled="!iscc || working"
          @click="copyCode"
        )
          UiIcon(:name="copied ? 'check' : 'copy'" :size="14")
          span(v-text="copied ? 'Copied' : 'Copy'")
      .units-label
        span(v-text="unitsLabel")
        .rule
      .unit-grid
        template(v-if="working")
          UnitField(
            v-for="(kind, index) in pendingKinds"
            :key="kind"
            :kind="kind"
            :state="specimen.status === 'uploading' ? 'queued' : 'hashing'"
            :code="pendingCode(index)"
            :bits="null"
            :selected="false"
          )
        template(v-else)
          UnitField(
            v-for="view in unitViews"
            :key="view.kind"
            :kind="view.kind"
            state="ready"
            :code="view.code"
            :bits="view.bits"
            :selected="view.kind === selected"
            @select="selected = view.kind"
          )
      .axis
        span ABSTRACT &amp; PERSISTENT
        .axis-line
        span CONCRETE &amp; VOLATILE
    UnitDetail(
      v-if="specimen.status === 'done' && selectedView"
      :specimen="specimen"
      :kind="selectedView.kind"
      :unit="selectedView.unit"
      @embed="(formData) => emit('embed', formData)"
    )
    .card-foot(v-if="specimen.status === 'done'")
      button.raw-toggle(
        type="button"
        :class="{ open: rawOpen }"
        @click="rawOpen = !rawOpen"
      )
        UiIcon(name="chevron-right" :size="13")
        span Raw result JSON
      .compare-cta(v-if="compareOptions.length")
        button.compare-btn(type="button" @click="onCompareClick")
          UiIcon(name="compare" :size="14")
          span Compare with another file
        .picker(v-if="pickerOpen")
          button.pick(
            v-for="option in compareOptions"
            :key="option.id"
            type="button"
            @click="pickCompare(option.id)"
          )
            span.pick-name(v-text="option.label")
            span.pick-code(v-text="option.iscc")
    .raw-json(v-if="rawOpen && specimen.status === 'done'")
      highlightjs(language="json" :code="rawJson")
</template>

<style scoped lang="scss">
.result-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 0.75rem;
  box-shadow:
    0 10px 24px -4px rgba(18, 54, 99, 0.14),
    0 4px 8px -4px rgba(18, 54, 99, 0.08);
  overflow: hidden;
}

// ---------- card head ----------

.card-head {
  padding: 1.1rem 1.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.ident {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-width: 0;
}

.thumb {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 0.5rem;
  object-fit: cover;
  flex-shrink: 0;

  &.glyph {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    color: var(--iscc-deep-navy);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.who {
  min-width: 0;
}

.name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #212529;
  word-break: break-all;
}

.facts {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 300;
  color: #6c757d;
  margin-top: 0.1rem;
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.chip-semantic {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #7a5c00;
  background: rgba(255, 195, 0, 0.16);
  border: 1px solid rgba(255, 195, 0, 0.55);
  border-radius: 9999px;
  padding: 0.3rem 0.7rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 9999px;
  padding: 0.32rem 0.8rem;
  font-family: var(--bs-font-monospace);
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.06em;

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  &.busy {
    background: rgba(0, 84, 178, 0.07);
    border: 1px solid rgba(0, 84, 178, 0.3);
    color: var(--iscc-blue);

    .dot {
      background: var(--iscc-blue);
      animation: pulse-dot 1.4s ease-in-out infinite;
    }
  }

  &.done {
    background: rgba(166, 219, 80, 0.18);
    border: 1px solid rgba(166, 219, 80, 0.55);
    color: #4d6e14;

    .dot {
      background: #79a832;
    }
  }

  &.fail {
    background: rgba(245, 97, 105, 0.1);
    border: 1px solid rgba(245, 97, 105, 0.45);
    color: #b3434a;

    .dot {
      background: var(--iscc-coral-red);
    }
  }
}

.icon-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
  background: none;
  color: #495057;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  &:hover {
    border-color: var(--iscc-blue);
    color: var(--iscc-blue);
  }
}

// ---------- error ----------

.alert-strip {
  margin: 0 1.75rem 1.25rem;
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  background: rgba(245, 97, 105, 0.08);
  border: 1px solid rgba(245, 97, 105, 0.4);
  border-radius: 0.65rem;
  padding: 0.8rem 1rem;
  font-size: 0.8rem;
  color: #8c3338;
  word-break: break-all;

  b {
    font-weight: 600;
  }
}

// ---------- navy readout strip ----------

.navy-strip {
  background-color: var(--iscc-deep-navy);
  padding: 1.25rem 1.75rem 1.5rem;
  position: relative;
  overflow: hidden;
}

.progress-track {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--iscc-bright-yellow);
  transition:
    width 0.2s linear,
    opacity 0.6s ease;
  z-index: 5;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 2px;
  background: linear-gradient(to right, transparent, #7ac2f7 30%, #7ac2f7 70%, transparent);
  box-shadow: 0 0 14px 3px rgba(122, 194, 247, 0.45);
  animation: scan-sweep 2.1s ease-in-out infinite alternate;
  z-index: 4;
  pointer-events: none;
}

.code-row {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.code-bar {
  flex: 1;
  min-width: 0;
  background-color: var(--iscc-coral-red);
  border-radius: 0.5rem;
  padding: 0.7rem 1rem;
  font-family: var(--bs-font-monospace);
  font-size: clamp(7px, 1.9vw, 17px);
  font-weight: 300;
  letter-spacing: -0.01em;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;

  &.working span {
    color: rgba(255, 255, 255, 0.45);
  }
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: var(--iscc-bright-yellow);
  color: var(--iscc-deep-navy);
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.5rem 0.95rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  flex-shrink: 0;

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
}

.units-label {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.9rem;
  margin-bottom: 0.5rem;

  span {
    font-family: var(--bs-font-monospace);
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    color: rgba(255, 255, 255, 0.6);
  }

  .rule {
    flex: 1;
    height: 1px;
    background: rgba(255, 255, 255, 0.15);
  }
}

.unit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.65rem;

  @media (max-width: 575.98px) {
    grid-template-columns: 1fr;
  }
}

.axis {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;

  span {
    font-family: var(--bs-font-monospace);
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    color: rgba(255, 255, 255, 0.55);
  }

  .axis-line {
    flex: 1;
    height: 2px;
    background: rgba(255, 195, 0, 0.6);
  }
}

// ---------- footer ----------

.card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 1.75rem;
  border-top: 1px solid #f1f3f5;
  background: #fcfcfd;
  flex-wrap: wrap;
}

.raw-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: none;
  border: none;
  color: #6c757d;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0;

  .ui-icon {
    transition: transform 0.15s ease;
  }

  &.open .ui-icon {
    transform: rotate(90deg);
  }
}

.compare-cta {
  position: relative;
}

.compare-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1.5px solid var(--iscc-blue);
  color: var(--iscc-blue);
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.45rem 0.9rem;
  border-radius: 9999px;
  cursor: pointer;

  &:hover {
    background: rgba(0, 84, 178, 0.06);
  }
}

.picker {
  position: absolute;
  right: 0;
  bottom: calc(100% + 0.4rem);
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  box-shadow: 0 10px 24px -4px rgba(18, 54, 99, 0.2);
  min-width: 16rem;
  max-height: 14rem;
  overflow-y: auto;
  z-index: 20;
}

.pick {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #f1f3f5;
  padding: 0.55rem 0.8rem;
  cursor: pointer;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: #f8f9fa;
  }

  .pick-name {
    display: block;
    font-size: 0.78rem;
    font-weight: 600;
    color: #212529;
    word-break: break-all;
  }

  .pick-code {
    display: block;
    font-family: var(--bs-font-monospace);
    font-size: 0.62rem;
    color: #adb5bd;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.raw-json {
  border-top: 1px solid #f1f3f5;
  max-height: 24rem;
  overflow: auto;

  :deep(pre) {
    margin: 0;
    padding: 1rem 1.75rem;
    font-size: 0.72rem;
  }
}

// ---------- comparison mode ----------

.compare-head {
  padding: 1rem 1.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.pair {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  flex-wrap: wrap;
}

.side {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
}

.side-tag {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 700;
  color: #6c757d;
  background: #f1f3f5;
  border-radius: 0.4rem;
  width: 1.4rem;
  height: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.thumb-mini {
  width: 2rem;
  height: 2rem;
  border-radius: 0.45rem;
  object-fit: cover;
  flex-shrink: 0;

  &.glyph {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    color: var(--iscc-deep-navy);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.code-mini {
  font-family: var(--bs-font-monospace);
  font-size: 0.66rem;
  font-weight: 300;
  color: #adb5bd;
}

.swap-glyph {
  color: #adb5bd;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.ghost-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border: 1px solid #dee2e6;
  background: none;
  color: #495057;
  font-size: 0.78rem;
  font-weight: 500;
  padding: 0.45rem 0.8rem;
  border-radius: 0.5rem;
  cursor: pointer;

  &:hover {
    border-color: var(--iscc-blue);
    color: var(--iscc-blue);
  }
}

.compare-legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 1.75rem;
  background: #fcfcfd;
  flex-wrap: wrap;
}

.legend-items {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;

  .swatch {
    width: 10px;
    height: 10px;
    border-radius: 2px;
  }

  span {
    font-size: 0.75rem;
    font-weight: 300;
    color: #6c757d;
  }
}

.legend-hint {
  font-size: 0.75rem;
  font-weight: 300;
  color: #adb5bd;
}
</style>
