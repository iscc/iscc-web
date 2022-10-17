<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  file: IsccWeb.FileUpload;
}>();

const emit = defineEmits<{
  (e: "remove-uploaded-file", file: IsccWeb.FileUpload): void;
}>();

const onCloseClick = () => {
  emit("remove-uploaded-file", props.file);
};

const working = computed(() => {
  return props.file.status !== "PROCESSED";
});
</script>

<template lang="pug">
.card
  .card-header
    ul.nav.nav-tabs.card-header-tabs
      li.nav-item
        a.nav-link.active(href="#") ISCC
      li.nav-item
        a.nav-link.disabled(href="#") DNA
    .btn-close-container
      button.btn-close(
        aria-label="Close"
        type="button"
        @click="onCloseClick"
      )
  .card-body
    .row.g-3
      .col
        h6.text-muted.mb-3(v-text="file.name")
    .row.g-3
      .col-12(v-if="file.status === 'PROCESSING' || file.status === 'UPLOADING'")
        .progress(style="height: 40px")
          .progress-bar.progress-bar-striped.progress-bar-animated(
            style="width: 100%"
            v-if="file.status === 'PROCESSING'"
          ) Upload finished, processing...
          .progress-bar(v-if="file.status === 'UPLOADING'" :style="`width: ${file.progress || 0}%`") Uploading...
      .col-12(v-if="file.isccMetadata?.iscc")
        .input-group
          .input-group-text ISCC-CODE
          input.form-control.font-monospace(
            type="text"
            readonly
            :value="file.isccMetadata?.iscc"
          )
      .col-12.col-md-3(v-if="file.isccMetadata?.thumbnail")
        img.img-thumbnail(:src="file.isccMetadata.thumbnail")
      .col(v-if="file.isccMetadata")
        .form-floating.mb-3
          input.form-control(
            type="text"
            :id="`name[${file.id}]`"
            :value="file.isccMetadata?.name"
            :disabled="working"
            placeholder="Name"
          )
          label(:for="`name[${file.id}]`") Name or title of the work
        .form-floating
          input.form-control(
            type="text"
            :id="`description[${file.id}]`"
            :value="file.isccMetadata?.description"
            :disabled="working"
            placeholder="Description"
          )
          label(:for="`description[${file.id}]`") Description of the work
</template>

<style scoped lang="scss">
.card-header {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;

  .nav {
    flex-grow: 1;
  }

  .btn-close-container {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
}

.card-body {
  .img-thumbnail {
    width: 100%;
  }
}
</style>
