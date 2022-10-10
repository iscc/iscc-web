<script setup lang="ts">
import { ref } from "vue";

import IsccHeader from "./components/IsccHeader.vue";
import UploadZone from "./components/UploadZone.vue";
import UploadedFile from "./components/UploadedFile.vue";

const uploadedMediaFiles = ref<Array<Api.IsccMetadata>>([]);

const onUploadSuccess = (isccMetadata: Api.IsccMetadata) => {
  uploadedMediaFiles.value.unshift(isccMetadata);
};

const onRemoveUploadedFile = (mediaId: string) => {
  uploadedMediaFiles.value = uploadedMediaFiles.value.filter((v) => v.media_id !== mediaId);
}
</script>

<template lang="pug">
div
  IsccHeader.mb-3
  .container
    .row
      .col
        hr
  UploadZone(@upload-success="onUploadSuccess")
  .container
    .row
      .col
        hr
  .container
    .row.mb-3(v-for="isccMetadata in uploadedMediaFiles" :key="isccMetadata.media_id")
      .col
        UploadedFile(:isccMetadata="isccMetadata" @remove-uploaded-file="onRemoveUploadedFile")
</template>

<style scoped lang="scss">
code {
  font-size: 0.75rem;
}
</style>
