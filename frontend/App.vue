<script setup lang="ts">
import { ref } from "vue";

import IsccHeader from "./components/IsccHeader.vue";
import UploadZone from "./components/UploadZone.vue";
import UploadedFile from "./components/UploadedFile.vue";
import IsccFooter from "./components/IsccFooter.vue";
import type { UppyFile } from "@uppy/core";
import { apiService } from "./services/api.service";

const uploadedMediaFiles = ref<Array<IsccWeb.FileUpload>>([]);

const updateUploadedMediaFile = (fileId: string, data: Partial<IsccWeb.FileUpload>) => {
  uploadedMediaFiles.value = uploadedMediaFiles.value.map((f) => {
    if (f.id == fileId) {
      return {
        ...f,
        ...data,
      };
    }

    return f;
  });
};

const loadHashBitsForFile = async (fileId: string, iscc: string) => {
  const isccDecomposition = await apiService.explainIscc(iscc);
  const hashBits = isccDecomposition.units.map((unit) => unit.hash_bits).join("");

  updateUploadedMediaFile(fileId, { hashBits });
};

const onFileAdded = (file: UppyFile) => {
  uploadedMediaFiles.value.unshift({
    id: file.id,
    name: file.name,
    progress: 0,
    status: "UPLOADING",
    isccMetadata: null,
    metadataChanged: false,
    error: null,
    hashBits: null,
  });
};

const onUploadProgress = (file: UppyFile, percentage: number) => {
  const data: Partial<IsccWeb.FileUpload> = {
    progress: percentage,
  };

  if (percentage > 99) {
    data.status = "PROCESSING";
  }

  updateUploadedMediaFile(file.id, data);
};

const onUploadError = (file: UppyFile, error: Error) => {
  updateUploadedMediaFile(file.id, {
    status: "ERROR",
    error: error,
  });
};

const onUploadSuccess = async (file: UppyFile, isccMetadata: Api.IsccMetadata) => {
  updateUploadedMediaFile(file.id, {
    progress: 100,
    status: "PROCESSED",
    isccMetadata: isccMetadata,
  });

  await loadHashBitsForFile(file.id, isccMetadata.iscc);
};

const onRemoveUploadedFile = (file: IsccWeb.FileUpload) => {
  uploadedMediaFiles.value = uploadedMediaFiles.value.filter((v) => v.id !== file.id);
};

const onUpdateMetadata = async (file: IsccWeb.FileUpload, formData: IsccWeb.MetadataFormData) => {
  updateUploadedMediaFile(file.id, {
    status: "UPDATING_METADATA",
  });

  try {
    const newMetadata = await apiService.embedMetadata(file.isccMetadata?.media_id, formData);

    updateUploadedMediaFile(file.id, {
      isccMetadata: newMetadata,
      metadataChanged: true,
      status: "PROCESSED",
      hashBits: null,
    });

    await loadHashBitsForFile(file.id, newMetadata.iscc);
  } catch (e) {
    updateUploadedMediaFile(file.id, {
      status: "ERROR",
      error: e,
    });
  }
};

const buildComparisonForFileAtIndex = (index: number) => {
  if (uploadedMediaFiles.value.length < 2) {
    return;
  }

  if (index > 1) {
    return;
  }

  const comparisonFileUpload = uploadedMediaFiles.value[index === 0 ? 1 : 0];

  return {
    name: comparisonFileUpload.name,
    hashBits: comparisonFileUpload.hashBits,
  };
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
    .row.mb-3(v-for="(file, index) in uploadedMediaFiles" :key="file.id")
      h2(v-if="uploadedMediaFiles.length > 1 && index == 0") Comparison
      h2(v-if="uploadedMediaFiles.length > 2 && index == 2") Previous uploads
      .col
        UploadedFile(
          :file="file"
          :comparison="buildComparisonForFileAtIndex(index)"
          @remove-uploaded-file="onRemoveUploadedFile"
          @update-metadata="onUpdateMetadata"
        )
    IsccFooter
</template>

<style scoped lang="scss">
code {
  font-size: 0.75rem;
}
</style>
