<script setup lang="ts">
import { ref } from "vue";

import IsccHeader from "./components/IsccHeader.vue";
import UploadZone from "./components/UploadZone.vue";

const uploadedMediaFiles = ref<Array<Api.IsccMetadata>>([]);

const onUploadSuccess = (isccMetadata: Api.IsccMetadata) => {
  uploadedMediaFiles.value.push(isccMetadata);
};
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
    .row.g-3
      .col-12.col-lg-6(v-for="isccMetadata in uploadedMediaFiles" :key="isccMetadata.media_id")
        .card
          .card-body
            h5.card-title(v-text="isccMetadata.media_id")
            h6.card-subtitle.text-muted(v-text="isccMetadata.name" :if="isccMetadata.name")
            p.card-text.overflow-scroll
              pre
                code(v-text="JSON.stringify(isccMetadata, null, 2)")
</template>

<style scoped lang="scss">
code {
  font-size: 0.75rem;
}
</style>
