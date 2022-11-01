<script setup lang="ts">
import Uppy from "@uppy/core";
import type { UppyFile } from "@uppy/utils";
import XhrUpload from "@uppy/xhr-upload";
import { Base64 } from "js-base64";
import { computed, onUnmounted, ref } from "vue";
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiFolderMultipleImage } from "@mdi/js";

const emit = defineEmits<{
  (e: "file-added", file: UppyFile): void;
  (e: "upload-progress", file: UppyFile, percentage: number): void;
  (e: "upload-error", file: UppyFile, error: Error): void;
  (e: "upload-success", file: UppyFile, isccMetadata: Api.IsccMetadata): void;
}>();

const uppy = computed(() =>
  new Uppy({ autoProceed: true })
    .use(XhrUpload, {
      endpoint: "/api/v1/iscc",
      formData: false,
      timeout: 0,
      headers: (file) => ({ "X-Upload-Filename": Base64.encode(file.name) }),
      getResponseError: (responseText, response: unknown) => {
        if (response instanceof XMLHttpRequest) {
          return new Error(`${(response as XMLHttpRequest).status}: ${responseText}`);
        }

        return new Error(responseText);
      },
    })
    .on("file-added", (file) => {
      emit("file-added", file);
    })
    .on("upload-success", (file, response) => {
      if (!file) {
        return;
      }

      const metadata: Api.IsccMetadata = response.body;
      emit("upload-success", file, metadata);
    })
    .on("upload-progress", (file, progress) => {
      if (!file) {
        return;
      }

      emit("upload-progress", file, Math.floor((progress.bytesUploaded / progress.bytesTotal) * 100));
    })
    .on("upload-error", (file, error) => {
      if (!file) {
        return;
      }

      emit("upload-error", file, error);
    })
);

onUnmounted(() => {
  uppy.value.close({ reason: "unmount" });
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
    }))
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
        button.btn.btn-primary.mt-3.mb-5(@click="input?.click()") or choose media file
</template>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions";
@import "~bootstrap/scss/_variables";

.upload-zone {
  text-align: center;
  background-color: $gray-300;
  border-radius: 20px;
  border: 2px dashed black;

  &.dragging {
    background-color: $gray-200;
  }

  input[type="file"] {
    display: none;
  }
}
</style>
