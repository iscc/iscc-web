<script setup lang="ts">
const props = defineProps<{
  isccMetadata: Api.IsccMetadata;
}>();

const emit = defineEmits<{
  (e: "remove-uploaded-file", mediaId: string): void;
}>();

const onCloseClick = () => {
  emit("remove-uploaded-file", props.isccMetadata.media_id);
};
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
        h6.text-muted.mb-3(v-text="isccMetadata.filename")
        .input-group.mb-3
          .input-group-text ISCC-CODE
          input.form-control.font-monospace(
            type="text"
            readonly
            :value="isccMetadata.iscc"
          )
    .row.g-3
      .col-12.col-md-3(v-if="isccMetadata.thumbnail")
        img.img-thumbnail(:src="isccMetadata.thumbnail")
      .col
        .form-floating.mb-3
          input.form-control(
            type="text"
            :id="`name[${isccMetadata.media_id}]`"
            :value="isccMetadata.name"
            placeholder="Name"
          )
          label(:for="`name[${isccMetadata.media_id}]`") Name or title of the work
        .form-floating
          input.form-control(
            type="text"
            :id="`description[${isccMetadata.media_id}]`"
            :value="isccMetadata.description"
            placeholder="Description"
          )
          label(:for="`description[${isccMetadata.media_id}]`") Description of the work
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
