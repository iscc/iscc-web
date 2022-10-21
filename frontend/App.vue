<script setup lang="ts">
import { ref } from "vue";

import IsccHeader from "./components/IsccHeader.vue";
import UploadZone from "./components/UploadZone.vue";
import UploadedFile from "./components/UploadedFile.vue";
import type { UppyFile } from "@uppy/core";

const uploadedMediaFiles = ref<Array<IsccWeb.FileUpload>>([]);

const onFileAdded = (file: UppyFile) => {
  uploadedMediaFiles.value.unshift({
    id: file.id,
    name: file.name,
    progress: 0,
    status: "UPLOADING",
    isccMetadata: null,
    error: null,
  });
};

const onUploadProgress = (file: UppyFile, percentage: number) => {
  uploadedMediaFiles.value.forEach((f) => {
    if (f.id == file.id) {
      f.progress = percentage;

      if (percentage > 99) {
        f.status = "PROCESSING";
      }
    }
  });
};

const onUploadError = (_file: UppyFile, error: Error) => {
  alert(`${error.name}: ${error.message}`);
};

const onUploadSuccess = (file: UppyFile, isccMetadata: Api.IsccMetadata) => {
  uploadedMediaFiles.value.forEach((f) => {
    if (f.id == file.id) {
      f.isccMetadata = isccMetadata;
      f.progress = 100;
      f.status = "PROCESSED";
    }
  });
};

const onRemoveUploadedFile = (file: IsccWeb.FileUpload) => {
  uploadedMediaFiles.value = uploadedMediaFiles.value.filter((v) => v.id !== file.id);
};
</script>

<template lang="pug">
div
  IsccHeader.mb-3
  UploadZone(
    @upload-success="onUploadSuccess"
    @upload-progress="onUploadProgress"
    @file-added="onFileAdded"
    @upload-error="onUploadError"
  )
  .container.mt-4
    .row.mb-3(v-for="file in uploadedMediaFiles" :key="file.id")
      .col
        UploadedFile(:file="file" @remove-uploaded-file="onRemoveUploadedFile")
</template>

<style scoped lang="scss">
code {
  font-size: 0.75rem;
}
</style>
