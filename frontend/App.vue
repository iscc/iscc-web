<script setup lang="ts">
// Single-page orchestrator: navy header, hero with the intake instrument, and an
// education strip that morphs in place into the decoder-readout feed once the
// first result lands (Concept 4 — Canvas × Decoder).
import { ref } from "vue";
import type { Meta, Body, UppyFile } from "@uppy/core";
import AppFooter from "./components/AppFooter.vue";
import AppHeader from "./components/AppHeader.vue";
import EducationStrip from "./components/EducationStrip.vue";
import IntakeCard from "./components/IntakeCard.vue";
import ResultCard from "./components/ResultCard.vue";
import UiIcon from "./components/UiIcon.vue";
import { apiService } from "./services/api.service";

const specimens = ref<IsccWeb.Specimen[]>([]);
let sequence = 0;

const findSpecimen = (id: string) => specimens.value.find((s) => s.id === id);

const cleanupSpecimen = (specimen: IsccWeb.Specimen) => {
  const mediaId = specimen.metadata?.media_id;
  if (mediaId && specimen.status === "done") {
    apiService.deleteMedia(mediaId).catch(() => undefined);
  }
  if (specimen.previewUrl && typeof URL.revokeObjectURL === "function") {
    URL.revokeObjectURL(specimen.previewUrl);
  }
};

const clearSpecimens = () => {
  for (const specimen of specimens.value) cleanupSpecimen(specimen);
  specimens.value = [];
};

const baseSpecimen = (partial: Partial<IsccWeb.Specimen> & Pick<IsccWeb.Specimen, "id" | "kind" | "label">) => {
  const specimen: IsccWeb.Specimen = {
    status: "processing",
    progress: 0,
    bytesUploaded: 0,
    bytesTotal: 0,
    typeHint: "",
    startedAt: performance.now(),
    elapsed: null,
    error: null,
    semantic: false,
    granular: false,
    metadata: null,
    explain: null,
    previewUrl: null,
    metadataChanged: false,
    embedBusy: false,
    embedError: null,
    compareWithId: null,
    compareSwapped: false,
    ...partial,
  };
  specimens.value.unshift(specimen);
  // Return the reactive proxy, not the raw object - mutations on the raw object
  // would update state without triggering a re-render.
  return specimens.value[0];
};

// Resolve the readout: store metadata, decompose the composite for bit-level
// units, stamp the elapsed time and settle the card.
const finalize = async (id: string, metadata: Api.IsccMetadata) => {
  const specimen = findSpecimen(id);
  if (!specimen) return;
  specimen.metadata = metadata;
  try {
    specimen.explain = await apiService.explainIscc(metadata.iscc);
  } catch {
    specimen.explain = null;
  }
  specimen.elapsed = (performance.now() - specimen.startedAt) / 1000;
  specimen.status = "done";
};

const fail = (id: string, message: string) => {
  const specimen = findSpecimen(id);
  if (!specimen) return;
  specimen.status = "error";
  specimen.error = message;
};

// --- file intake -----------------------------------------------------------------

const onFileAdded = (
  file: UppyFile<Meta, Body>,
  options: { semantic: boolean; granular: boolean; previewUrl: string | null },
) => {
  baseSpecimen({
    id: file.id,
    kind: "file",
    label: file.name ?? "file",
    status: "uploading",
    bytesTotal: file.size ?? 0,
    typeHint: file.type ?? "",
    semantic: options.semantic,
    granular: options.granular,
    previewUrl: options.previewUrl,
  });
};

const onUploadProgress = (fileId: string, progress: { percent: number; bytesUploaded: number; bytesTotal: number }) => {
  const specimen = findSpecimen(fileId);
  if (!specimen || specimen.status === "error") return;
  specimen.progress = progress.percent;
  specimen.bytesUploaded = progress.bytesUploaded;
  if (progress.bytesTotal) specimen.bytesTotal = progress.bytesTotal;
  if (progress.percent >= 100) specimen.status = "processing";
};

const onUploadError = (fileId: string, message: string) => fail(fileId, message);

const onUploadSuccess = async (fileId: string, metadata: Api.IsccMetadata) => {
  const specimen = findSpecimen(fileId);
  if (!specimen || specimen.status === "error") return;
  specimen.status = "processing";
  await finalize(fileId, metadata);
};

// --- text intake -------------------------------------------------------------------

const onTextSubmit = async (text: string, options: { semantic: boolean; granular: boolean }) => {
  const specimen = baseSpecimen({
    id: `text-${++sequence}`,
    kind: "text",
    label: "Pasted text",
    typeHint: "text/plain",
    semantic: options.semantic,
    granular: options.granular,
  });
  try {
    const metadata = await apiService.createIsccFromText(text, options.semantic, options.granular);
    await finalize(specimen.id, metadata);
  } catch (error) {
    fail(specimen.id, error instanceof Error ? error.message : String(error));
  }
};

// --- code intake ---------------------------------------------------------------------

const onCodeSubmit = async (iscc: string) => {
  const specimen = baseSpecimen({ id: `code-${++sequence}`, kind: "code", label: "Decoded ISCC" });
  try {
    specimen.explain = await apiService.explainIscc(iscc);
    specimen.elapsed = (performance.now() - specimen.startedAt) / 1000;
    specimen.status = "done";
  } catch (error) {
    fail(specimen.id, error instanceof Error ? error.message : String(error));
  }
};

// --- per-card actions ------------------------------------------------------------------

const onEmbed = async (specimen: IsccWeb.Specimen, formData: IsccWeb.MetadataFormData) => {
  const mediaId = specimen.metadata?.media_id;
  if (!mediaId) return;
  specimen.embedBusy = true;
  specimen.embedError = null;
  try {
    const metadata = await apiService.embedMetadata(mediaId, formData);
    specimen.metadata = metadata;
    specimen.metadataChanged = true;
    try {
      specimen.explain = await apiService.explainIscc(metadata.iscc);
    } catch {
      specimen.explain = null;
    }
  } catch (error) {
    specimen.embedError = error instanceof Error ? error.message : String(error);
  } finally {
    specimen.embedBusy = false;
  }
};

const onRemove = (specimen: IsccWeb.Specimen) => {
  cleanupSpecimen(specimen);
  specimens.value = specimens.value.filter((s) => s.id !== specimen.id);
  for (const other of specimens.value) {
    if (other.compareWithId === specimen.id) {
      other.compareWithId = null;
      other.compareSwapped = false;
    }
  }
};

const onCompare = (specimen: IsccWeb.Specimen, targetId: string) => {
  specimen.compareWithId = targetId;
  specimen.compareSwapped = false;
};

const onEject = (specimen: IsccWeb.Specimen) => {
  specimen.compareWithId = null;
  specimen.compareSwapped = false;
};

const onSwap = (specimen: IsccWeb.Specimen) => {
  specimen.compareSwapped = !specimen.compareSwapped;
};

const compareTargetFor = (specimen: IsccWeb.Specimen) => {
  if (!specimen.compareWithId) return null;
  const target = findSpecimen(specimen.compareWithId);
  return target && target.status === "done" && target.explain ? target : null;
};

const compareOptionsFor = (specimen: IsccWeb.Specimen) =>
  specimens.value
    .filter((other) => other.id !== specimen.id && other.status === "done" && other.explain)
    .map((other) => ({
      id: other.id,
      label: other.label,
      iscc: other.metadata?.iscc ?? other.explain?.iscc ?? "",
    }));
</script>

<template lang="pug">
.app-shell
  AppHeader
  section.hero.grain
    .container-xl
      .hero-grid
        .intake-col
          IntakeCard(
            @file-added="onFileAdded"
            @upload-progress="onUploadProgress"
            @upload-error="onUploadError"
            @upload-success="onUploadSuccess"
            @text-submit="onTextSubmit"
            @code-submit="onCodeSubmit"
            @mode-change="clearSpecimens"
          )
        .copy-col
          .iso-badge
            UiIcon(name="check-circle" :size="13")
            span ISO 24138:2024
          h1.hero-title The #[span.accent DNA] of your digital content#[span.accent .]
          p.hero-sub An ISCC is a fingerprint generated #[b from the content itself] — no registry, no signup. Drop a file and read its code layer by layer.
          ul.hero-points
            li
              UiIcon(
                name="shield"
                :size="15"
                :stroke-width="2.2"
              )
              span Files stay private to you and are #[b auto-deleted after one hour]
            li
              UiIcon(
                name="image"
                :size="15"
                :stroke-width="2.2"
              )
              span Text, image, audio &amp; video — anything else still gets a Data + Instance code
  main.feed
    .container-xl
      EducationStrip(v-if="!specimens.length")
      .results(v-else)
        ResultCard(
          v-for="specimen in specimens"
          :key="specimen.id"
          :specimen="specimen"
          :compare-target="compareTargetFor(specimen)"
          :compare-options="compareOptionsFor(specimen)"
          @remove="onRemove(specimen)"
          @embed="(formData) => onEmbed(specimen, formData)"
          @compare="(targetId) => onCompare(specimen, targetId)"
          @eject="onEject(specimen)"
          @swap="onSwap(specimen)"
        )
  AppFooter
</template>

<style scoped lang="scss">
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.hero {
  background-color: var(--iscc-blue);
  padding: 2.75rem 0 3.25rem;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 3rem;
  align-items: start;

  @media (max-width: 991.98px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

.copy-col {
  color: #ffffff;
}

.iso-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  padding: 0.35rem 0.8rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 1.1rem;
}

.hero-title {
  margin: 0 0 1rem;
  font-size: clamp(1.8rem, 3.4vw, 2.5rem);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.015em;

  .accent {
    color: var(--iscc-bright-yellow);
  }
}

.hero-sub {
  margin: 0 0 1.35rem;
  color: rgba(255, 255, 255, 0.94);
  font-size: 0.94rem;
  font-weight: 300;
  line-height: 1.6;
  max-width: 26rem;

  b {
    font-weight: 600;
    color: #ffffff;
  }
}

.hero-points {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;

  li {
    display: flex;
    gap: 0.55rem;
    align-items: flex-start;
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.82rem;
    font-weight: 300;

    .ui-icon {
      margin-top: 2px;
      color: var(--iscc-lime-green);
    }

    &:last-child .ui-icon {
      color: var(--iscc-light-cyan);
    }

    b {
      font-weight: 500;
      color: #ffffff;
    }
  }
}

.feed {
  flex: 1;
  padding: 2.5rem 0 3.5rem;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>
