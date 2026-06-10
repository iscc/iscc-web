<script setup lang="ts">
import Uppy from "@uppy/core";
import type { Meta, Body, UppyFile } from "@uppy/core";
import XhrUpload from "@uppy/xhr-upload";
import { Base64 } from "js-base64";
import { computed, onUnmounted, ref } from "vue";
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiFolderMultipleImage } from "@mdi/js";

const emit = defineEmits<{
  (e: "file-added", file: UppyFile<Meta, Body>): void;
  (e: "upload-progress", file: UppyFile<Meta, Body>, percentage: number): void;
  (e: "upload-error", file: UppyFile<Meta, Body>, error: Error): void;
  (e: "upload-success", file: UppyFile<Meta, Body>, isccMetadata: Api.IsccMetadata): void;
}>();

const semantic = ref<boolean>(false);
const granular = ref<boolean>(false);

// Resolved per upload so toggle changes apply without rebuilding the Uppy instance
const uploadEndpoint = () => {
  const params = new URLSearchParams();
  if (semantic.value) params.set("semantic", "true");
  if (granular.value) params.set("granular", "true");
  const query = params.toString();
  return "/api/v1/iscc" + (query ? `?${query}` : "");
};

const uppy = computed(() =>
  new Uppy<Meta, Body>({ autoProceed: true })
    .use(XhrUpload, {
      endpoint: uploadEndpoint,
      formData: false,
      timeout: 0,
      headers: (file) => ({ "X-Upload-Filename": Base64.encode(file.name ?? "") }),
      // Fail fast: Uppy 5 would otherwise silently re-upload the full body 3 times
      shouldRetry: () => false,
    })
    .on("file-added", (file) => {
      emit("file-added", file);
    })
    .on("upload-success", (file, response) => {
      if (!file) return;
      const metadata = response.body as unknown as Api.IsccMetadata;
      emit("upload-success", file, metadata);
    })
    .on("upload-progress", (file, progress) => {
      if (!file) return;
      const total = progress.bytesTotal ?? 1;
      emit("upload-progress", file, Math.floor((progress.bytesUploaded / total) * 100));
    })
    .on("upload-error", (file, error, response) => {
      if (!file) return;
      // xhr-upload 5 passes the raw XMLHttpRequest here (its declared type is wrong)
      const xhr = response as unknown as XMLHttpRequest | undefined;
      const message = xhr?.status ? `${xhr.status}: ${xhr.responseText || error.message}` : error.message;
      emit("upload-error", file, new Error(message));
    }),
);

onUnmounted(() => {
  uppy.value.destroy();
});

const onInputChange = () => {
  if (!input.value || !input.value.files) {
    return;
  }

  handleFiles(input.value.files);
};

const onDragEnter = (e: Event) => {
  e.preventDefault();
  e.stopPropagation();

  dragging.value = true;
};
const onDragLeave = (e: Event) => {
  e.preventDefault();
  e.stopPropagation();

  dragging.value = false;
};
const onDragOver = (e: Event) => {
  e.preventDefault();
  e.stopPropagation();
};

const onDrop = (e: DragEvent) => {
  e.stopPropagation();
  e.preventDefault();

  dragging.value = false;

  if (!e.dataTransfer) {
    return;
  }

  handleFiles(e.dataTransfer.files);
};

const handleFiles = (fl: FileList) => {
  uppy.value.addFiles(
    Array.from(fl).map((f) => ({
      name: f.name,
      type: f.type,
      data: f,
      meta: {
        relativePath: f.webkitRelativePath,
      },
    })),
  );
};

const input = ref<InstanceType<typeof HTMLInputElement> | null>(null);
const dragging = ref<boolean>(false);
</script>

<template lang="pug">
.container
  .row
    .col
      .upload-zone(
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @dragover="onDragOver"
        @drop="onDrop"
        @click="input?.click()"
        :class="dragging ? 'dragging' : ''"
      )
        input(
          type="file"
          ref="input"
          multiple
          @change="onInputChange"
        )
        h2.mt-5
          SvgIcon.me-3(
            type="mdi"
            :path="mdiFolderMultipleImage"
            size="48"
          )
          span Drag & Drop
        button.btn.btn-primary.mt-3.mb-4(@click.stop="input?.click()") or choose media file
        .upload-options.d-flex.flex-column.flex-sm-row.justify-content-center.gap-2.gap-sm-4.pb-4(@click.stop)
          .form-check.form-switch
            input#semantic-toggle.form-check-input(type="checkbox" v-model="semantic")
            label.form-check-label(
              for="semantic-toggle"
              v-tooltip="'Add experimental Semantic-Code ISCC-UNITs for text and image content'"
            ) Semantic ISCC-UNITs
          .form-check.form-switch
            input#granular-toggle.form-check-input(type="checkbox" v-model="granular")
            label.form-check-label(
              for="granular-toggle"
              v-tooltip="'Add experimental granular simprint features for text content'"
            ) Granular simprints
</template>

<style scoped lang="scss">
.upload-zone {
  text-align: center;
  background-color: #ffffff;
  border-radius: 20px;
  border: 2px dashed var(--iscc-blue);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: #f8f9fa;
  }

  &.dragging {
    background-color: #e9ecef;
    border-style: solid;
    border-color: var(--iscc-sky-blue);
  }

  h2 {
    color: var(--iscc-deep-navy);
  }

  input[type="file"] {
    display: none;
  }

  .upload-options {
    .form-check-label {
      color: var(--iscc-deep-navy);
      font-size: 0.875rem;
    }
  }
}
</style>
