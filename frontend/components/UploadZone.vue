<script setup lang="ts">
import { Dashboard } from "@uppy/vue";

import "@uppy/core/dist/style.css";
import "@uppy/dashboard/dist/style.css";

import Uppy from "@uppy/core";
import type { UppyFile } from "@uppy/utils";
import Webcam from "@uppy/webcam";
import XhrUpload from "@uppy/xhr-upload";
import UppyDashboard from "@uppy/dashboard";
import { Base64 } from "js-base64";
import { computed, onUnmounted } from "vue";

const emit = defineEmits<{
  (e: "file-added", file: UppyFile): void;
  (e: "upload-progress", file: UppyFile, percentage: number): void;
  (e: "upload-error", file: UppyFile, error: Error): void;
  (e: "upload-success", file: UppyFile, isccMetadata: Api.IsccMetadata): void;
}>();

const uppy = computed(() =>
  new Uppy({ autoProceed: true })
    .use(UppyDashboard)
    .use(Webcam)
    .use(XhrUpload, {
      endpoint: "/api/v1/iscc",
      formData: false,
      timeout: 0,
      headers: (file) => ({ "X-Upload-Filename": Base64.encode(file.name) }),
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

      emit("upload-progress", file, Math.floor(progress.bytesUploaded / progress.bytesTotal * 100));
    })
    .on("upload-error", (file, error) => {
      if (!file) {
        return;
      }

      emit("upload-error", file, error);
    })
);

onUnmounted(() => {
  // fix tupes: https://github.com/transloadit/uppy/issues/4126
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (uppy.value.close as any)({ reason: "unmount" });
});
</script>

<template lang="pug">
.container
  Dashboard(
    :uppy="uppy"
    :plugins="['Webcam', 'XhrUpload']"
    width="100%"
  )
</template>

<style scoped lang="scss"></style>
