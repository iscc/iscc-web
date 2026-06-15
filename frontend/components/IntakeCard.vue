<script setup lang="ts">
// Intake instrument: three input modes (media file, plain text, ISCC code) plus the
// generation toggles. Owns the Uppy uploader and the page-wide drop catcher.
import Uppy from "@uppy/core";
import type { Meta, Body, UppyFile } from "@uppy/core";
import XhrUpload from "@uppy/xhr-upload";
import { Base64 } from "js-base64";
import { computed, onMounted, onUnmounted, ref } from "vue";
import { normalizeIscc } from "../lib/iscc";
import { apiService } from "../services/api.service";
import UiIcon from "./UiIcon.vue";

type IntakeMode = "file" | "text" | "code";

const emit = defineEmits<{
  (
    e: "file-added",
    file: UppyFile<Meta, Body>,
    options: { semantic: boolean; granular: boolean; previewUrl: string | null },
  ): void;
  (
    e: "upload-progress",
    fileId: string,
    progress: { percent: number; bytesUploaded: number; bytesTotal: number },
  ): void;
  (e: "upload-error", fileId: string, message: string): void;
  (e: "upload-success", fileId: string, metadata: Api.IsccMetadata): void;
  (e: "text-submit", text: string, options: { semantic: boolean; granular: boolean }): void;
  (e: "code-submit", iscc: string): void;
  (e: "mode-change", mode: IntakeMode): void;
}>();

const tab = ref<IntakeMode>("file");
const semantic = ref(false);
const granular = ref(false);
const text = ref("");
const codeInput = ref("");
const fileInput = ref<HTMLInputElement | null>(null);

// --- file intake (Uppy) ------------------------------------------------------

// Client-side object URL so images preview instantly, while still uploading.
const previewFor = (file: UppyFile<Meta, Body>): string | null => {
  if (!file.type?.startsWith("image/") || typeof URL.createObjectURL !== "function") return null;
  try {
    return URL.createObjectURL(file.data as Blob);
  } catch {
    return null;
  }
};

// Re-adding the same file must work (compare an edited copy with the original),
// so every add gets a unique id instead of Uppy's content-derived one.
let fileCounter = 0;

const uppy = new Uppy<Meta, Body>({
  autoProceed: true,
  onBeforeFileAdded: (file) => ({ ...file, id: `${file.id}-${++fileCounter}` }),
})
  .use(XhrUpload, {
    // Resolved per upload so toggle changes apply without rebuilding the Uppy instance.
    // Params are always sent explicitly - omitting them would fall back to the service
    // defaults (semantic off, granular on), decoupling the toggles from server config.
    endpoint: () => apiService.isccEndpoint(semantic.value, granular.value),
    formData: false,
    timeout: 0,
    headers: (file) => ({ "X-Upload-Filename": Base64.encode(file.name ?? "") }),
    // Fail fast: Uppy 5 would otherwise silently re-upload the full body 3 times
    shouldRetry: () => false,
  })
  .on("file-added", (file) => {
    emit("file-added", file, { semantic: semantic.value, granular: granular.value, previewUrl: previewFor(file) });
  })
  .on("upload-progress", (file, progress) => {
    if (!file) return;
    const total = progress.bytesTotal ?? 1;
    emit("upload-progress", file.id, {
      percent: Math.floor((progress.bytesUploaded / total) * 100),
      bytesUploaded: progress.bytesUploaded,
      bytesTotal: progress.bytesTotal ?? 0,
    });
  })
  .on("upload-error", (file, error, response) => {
    if (!file) return;
    // xhr-upload 5 passes the raw XMLHttpRequest here (its declared type is wrong)
    const xhr = response as unknown as XMLHttpRequest | undefined;
    const message = xhr?.status ? `${xhr.status}: ${xhr.responseText || error.message}` : error.message;
    emit("upload-error", file.id, message);
  })
  .on("upload-success", (file, response) => {
    if (!file) return;
    emit("upload-success", file.id, response.body as unknown as Api.IsccMetadata);
  });

onUnmounted(() => {
  uppy.destroy();
});

const setTab = (next: IntakeMode) => {
  if (tab.value === next) return;
  tab.value = next;
  emit("mode-change", next);
};

const addFiles = (list: FileList) => {
  setTab("file");
  uppy.addFiles(Array.from(list).map((f) => ({ name: f.name, type: f.type, data: f })));
};

const onInputChange = () => {
  if (!fileInput.value?.files?.length) return;
  addFiles(fileInput.value.files);
  fileInput.value.value = "";
};

// --- page-wide drop catcher ---------------------------------------------------

const dragDepth = ref(0);
const pageDrag = computed(() => dragDepth.value > 0);

const hasFiles = (e: DragEvent) => Array.from(e.dataTransfer?.types ?? []).includes("Files");
const onWinDragEnter = (e: DragEvent) => {
  if (!hasFiles(e)) return;
  e.preventDefault();
  dragDepth.value++;
};
const onWinDragOver = (e: DragEvent) => {
  if (hasFiles(e)) e.preventDefault();
};
const onWinDragLeave = (e: DragEvent) => {
  if (!hasFiles(e)) return;
  dragDepth.value = Math.max(0, dragDepth.value - 1);
};
const onWinDrop = (e: DragEvent) => {
  if (!hasFiles(e)) return;
  e.preventDefault();
  dragDepth.value = 0;
  if (e.dataTransfer?.files.length) addFiles(e.dataTransfer.files);
};

onMounted(() => {
  window.addEventListener("dragenter", onWinDragEnter);
  window.addEventListener("dragover", onWinDragOver);
  window.addEventListener("dragleave", onWinDragLeave);
  window.addEventListener("drop", onWinDrop);
});
onUnmounted(() => {
  window.removeEventListener("dragenter", onWinDragEnter);
  window.removeEventListener("dragover", onWinDragOver);
  window.removeEventListener("dragleave", onWinDragLeave);
  window.removeEventListener("drop", onWinDrop);
});

// --- text intake ----------------------------------------------------------------

const canSubmitText = computed(() => text.value.trim().length > 0);
const submitText = () => {
  if (!canSubmitText.value) return;
  emit("text-submit", text.value, { semantic: semantic.value, granular: granular.value });
};

// --- code intake ----------------------------------------------------------------

const normalizedCode = computed(() => normalizeIscc(codeInput.value));
const codeState = computed(() => (!codeInput.value.trim() ? "empty" : normalizedCode.value ? "valid" : "invalid"));
const codeHint = computed(() =>
  codeState.value === "empty"
    ? "validates as you type — prefix optional"
    : codeState.value === "valid"
      ? "ready to decode"
      : "not a valid ISCC yet",
);
const submitCode = () => {
  if (!normalizedCode.value) return;
  emit("code-submit", normalizedCode.value);
};
</script>

<template lang="pug">
.intake-card
  .intake-tabs
    button.intake-tab(
      type="button"
      :class="{ active: tab === 'file' }"
      @click="setTab('file')"
    )
      UiIcon(name="upload" :size="15")
      span Media file
    button.intake-tab(
      type="button"
      :class="{ active: tab === 'text' }"
      @click="setTab('text')"
    )
      UiIcon(name="type" :size="15")
      span Plain text
    button.intake-tab(
      type="button"
      :class="{ active: tab === 'code' }"
      @click="setTab('code')"
    )
      UiIcon(name="search" :size="15")
      span ISCC code
  .intake-body
    template(v-if="tab === 'file'")
      .drop-zone(
        :class="{ active: pageDrag }"
        role="button"
        tabindex="0"
        @click="fileInput?.click()"
        @keydown.enter="fileInput?.click()"
      )
        input.visually-hidden(
          type="file"
          multiple
          ref="fileInput"
          data-testid="file-input"
          @change="onInputChange"
        )
        .drop-icon
          UiIcon(name="upload" :size="22")
        .drop-title Drag &amp; drop media files
        .drop-sub
          | or #[span.browse browse] — multiple files OK, ISCC generates on add
    template(v-else-if="tab === 'text'")
      textarea.text-input(v-model="text" placeholder="Paste or type plain text — an article, a post, a chapter…")
      .row-actions
        span.input-note UTF-8 · uploaded as pasted-text.txt · {{ text.length.toLocaleString() }} characters
        button.btn-go(
          type="button"
          :disabled="!canSubmitText"
          @click="submitText"
        )
          span Generate ISCC
          UiIcon(name="arrow-right" :size="14")
    template(v-else)
      input.code-input(
        v-model="codeInput"
        type="text"
        spellcheck="false"
        placeholder="ISCC:KECWN77F73NA44D7BNDLJCRJ3M2YQGCK…"
        @keyup.enter="submitCode"
      )
      .row-actions
        .d-flex.align-items-center.gap-2
          .valid-dot(:class="codeState")
          span.input-note(v-text="codeHint")
        button.btn-go(
          type="button"
          :disabled="codeState !== 'valid'"
          @click="submitCode"
        )
          span Decode code
          UiIcon(name="arrow-right" :size="14")
      .code-help
        | No upload needed — the code itself carries its units. You get the same readout:
        | unit fields, bits and per-layer explanations. File-specific panels stay hidden.
    .intake-toggles(v-if="tab !== 'code'")
      .toggle-row
        .form-check.form-switch.m-0
          input#semantic-toggle.form-check-input(type="checkbox" v-model="semantic")
        .toggle-text
          label.toggle-label(for="semantic-toggle")
            span Semantic code
            span.chip-experimental EXPERIMENTAL
          .toggle-desc Adds a 5th unit from ML embeddings of #[i meaning]. Slower; the result is not a plain ISO 24138 code.
      .toggle-row
        .form-check.form-switch.m-0
          input#granular-toggle.form-check-input(type="checkbox" v-model="granular")
        .toggle-text
          label.toggle-label(for="granular-toggle")
            span Granular simprints
          .toggle-desc Per-chunk fingerprints of text — enables matching fragments inside a document.
.drop-catcher(v-if="pageDrag")
  .drop-ring
    UiIcon(name="upload" :size="26")
    .drop-big Drop anywhere
    .drop-small files join the feed and decode on arrival
</template>

<style scoped lang="scss">
.intake-card {
  background: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.intake-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-bottom: 1px solid #e9ecef;
}

.intake-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.8rem 0;
  font-size: 0.82rem;
  font-weight: 500;
  color: #6c757d;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition:
    color 0.15s ease,
    border-color 0.15s ease;

  &.active {
    color: var(--iscc-blue);
    border-bottom-color: var(--iscc-blue);
    font-weight: 600;
  }
}

.intake-body {
  padding: 1.35rem 1.5rem 1.5rem;
}

.drop-zone {
  border: 2px dashed #ced4da;
  border-radius: 0.65rem;
  background: #f8f9fa;
  padding: 2.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease,
    box-shadow 0.15s ease;

  &:hover {
    border-color: var(--iscc-blue);
  }

  &.active {
    border: 2px solid var(--iscc-blue);
    background: rgba(0, 84, 178, 0.07);
    box-shadow: 0 0 0 4px rgba(0, 84, 178, 0.14);
  }

  .drop-icon {
    width: 2.9rem;
    height: 2.9rem;
    border-radius: 0.65rem;
    background: rgba(0, 84, 178, 0.08);
    color: var(--iscc-blue);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .drop-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #212529;
  }

  .drop-sub {
    font-size: 0.76rem;
    font-weight: 300;
    color: #6c757d;

    .browse {
      color: var(--iscc-blue);
      font-weight: 500;
      text-decoration: underline;
      text-underline-offset: 2px;
    }
  }
}

.text-input {
  width: 100%;
  box-sizing: border-box;
  height: 7.5rem;
  resize: none;
  font-size: 0.82rem;
  font-weight: 300;
  line-height: 1.6;
  padding: 0.75rem 0.9rem;
  border: 1px solid #ced4da;
  border-radius: 0.65rem;
  background: #f8f9fa;
  color: #212529;
  outline: none;
  display: block;

  &:focus {
    border-color: var(--iscc-blue);
  }
}

.code-input {
  width: 100%;
  box-sizing: border-box;
  font-family: var(--bs-font-monospace);
  font-size: 0.78rem;
  letter-spacing: -0.01em;
  padding: 0.75rem 0.9rem;
  border: 1px solid #ced4da;
  border-radius: 0.65rem;
  background: #f8f9fa;
  color: #212529;
  outline: none;

  &:focus {
    border-color: var(--iscc-blue);
  }
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.65rem;
}

.input-note {
  font-family: var(--bs-font-monospace);
  font-size: 0.69rem;
  font-weight: 300;
  color: #adb5bd;
}

.btn-go {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: var(--iscc-blue);
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.55rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  flex-shrink: 0;

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
}

.valid-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ced4da;
  flex-shrink: 0;

  &.valid {
    background: var(--iscc-lime-green);
  }

  &.invalid {
    background: var(--iscc-coral-red);
  }
}

.code-help {
  margin-top: 0.85rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.65rem;
  padding: 0.75rem 0.9rem;
  font-size: 0.76rem;
  font-weight: 300;
  line-height: 1.55;
  color: #6c757d;
}

.intake-toggles {
  margin-top: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.toggle-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;

  .form-check-input {
    cursor: pointer;
  }
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #212529;
  cursor: pointer;
}

.chip-experimental {
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: #7a5c00;
  background: rgba(255, 195, 0, 0.25);
  border: 1px solid rgba(255, 195, 0, 0.6);
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
}

.toggle-desc {
  font-size: 0.76rem;
  font-weight: 300;
  color: #6c757d;
  margin-top: 0.1rem;
}

.drop-catcher {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(18, 54, 99, 0.62);
  pointer-events: none;

  .drop-ring {
    position: absolute;
    inset: 12px;
    border: 2px dashed rgba(255, 255, 255, 0.8);
    border-radius: 0.65rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #ffffff;
  }

  .drop-big {
    font-size: 1rem;
    font-weight: 600;
  }

  .drop-small {
    font-family: var(--bs-font-monospace);
    font-size: 0.69rem;
    font-weight: 300;
    color: rgba(255, 255, 255, 0.75);
  }
}
</style>
