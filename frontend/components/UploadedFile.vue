<script setup lang="ts">
import { computed, ref, watch } from "vue";
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiContentSave } from "@mdi/js";
import "highlight.js/styles/github.css";

const props = defineProps<{
  file: IsccWeb.FileUpload;
  comparison?: {
    name: string;
    hashBits?: Array<string>;
  };
}>();

const emit = defineEmits<{
  (e: "remove-uploaded-file", file: IsccWeb.FileUpload): void;
  (e: "update-metadata", file: IsccWeb.FileUpload, metadata: IsccWeb.MetadataFormData): void;
}>();

const onCloseClick = () => {
  emit("remove-uploaded-file", props.file);
};

const onUpdateMetadataClick = async () => {
  emit("update-metadata", props.file, formData.value);
};

const onDownloadClick = () => {
  window.location.href = `/api/v1/media/${props.file.isccMetadata.media_id}`;
};

const working = computed(() => {
  return props.file.status !== "PROCESSED" && props.file.status !== "ERROR";
});

const formData = ref<IsccWeb.MetadataFormData>({
  name: props.file.isccMetadata?.name,
  description: props.file.isccMetadata?.description,
});

const currentTab = ref<"iscc" | "dna" | "raw-metadata">("iscc");

watch(
  () => props.file,
  (newFile, oldFile) => {
    if (!newFile.isccMetadata || JSON.stringify(newFile.isccMetadata) === JSON.stringify(oldFile.isccMetadata)) {
      return;
    }

    formData.value.name = newFile.isccMetadata.name;
    formData.value.description = newFile.isccMetadata.description;
  },
  { deep: true }
);

const hashBitComparisonClass = (hashBit: string, index: number) => {
  if (!props.comparison || !props.comparison.hashBits) {
    return "";
  }

  if (props.comparison.hashBits[index] !== hashBit) {
    return "unequal";
  } else {
    return "equal";
  }
};
</script>

<template lang="pug">
.card
  .card-header
    ul.nav.nav-tabs.card-header-tabs
      li.nav-item
        a.nav-link(
          href="#"
          @click="currentTab = 'iscc'"
          :class="currentTab === 'iscc' ? 'active' : ''"
        ) ISCC
      li.nav-item
        a.nav-link(
          href="#"
          @click="currentTab = 'dna'"
          :class="currentTab === 'dna' ? 'active' : ''"
        ) DNA
      li.nav-item
        a.nav-link(
          href="#"
          @click="currentTab = 'raw-metadata'"
          :class="currentTab === 'raw-metadata' ? 'active' : ''"
        ) Raw ISCC metadata
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
      .col-12(v-if="file.status === 'ERROR'")
        .alert.alert-danger.mb-0(v-text="file.error")
      .col-12(v-if="file.status === 'PROCESSING' || file.status === 'UPLOADING'")
        .progress(style="height: 40px")
          .progress-bar.progress-bar-striped.progress-bar-animated(
            style="width: 100%"
            v-if="file.status === 'PROCESSING'"
          ) Upload finished, processing...
          .progress-bar(v-if="file.status === 'UPLOADING'" :style="`width: ${file.progress || 0}%`") Uploading...
      .col-12(v-if="file.isccMetadata?.iscc")
        .font-monospace.iscc-code(v-text="file.isccMetadata?.iscc")
      template(v-if="currentTab === 'iscc'")
        .col-12.col-sm-3.col-lg-2(v-if="file.isccMetadata?.thumbnail")
          img.img-thumbnail(:src="file.isccMetadata.thumbnail")
        .col(v-if="file.isccMetadata")
          .form-floating.mb-3
            input.form-control(
              type="text"
              :id="`name[${file.id}]`"
              :disabled="working"
              v-model="formData.name"
              placeholder="Name"
            )
            label(:for="`name[${file.id}]`") Name or title of the work
          .form-floating.mb-3
            input.form-control(
              type="text"
              :id="`description[${file.id}]`"
              :disabled="working"
              v-model="formData.description"
              placeholder="Description"
            )
            label(:for="`description[${file.id}]`") Description of the work
          .row.g-3
            .col
              button.btn.btn-primary.w-100.d-flex.flex-row.align-items-center.justify-content-center(
                @click="onUpdateMetadataClick"
                :disabled="working"
              )
                SvgIcon.me-1(
                  type="mdi"
                  :path="mdiContentSave"
                  size="16"
                )
                span Update metadata & generate ISCC
            .col-6(v-if="file.metadataChanged")
              button.btn.btn-primary.w-100(@click="onDownloadClick" :disabled="working") Download updated file
      .dna.d-flex.flex-column.align-items-center.justify-content-center(v-else-if="currentTab === 'dna'")
        .comparison(v-if="comparison")
          span(v-text="`Compared to ${comparison.name}. Green = equal bit, red = unequal bit.`")
        .hash-bits(v-if="file.hashBits")
          .hash-bit(
            v-for="(hashBit, index) in file.hashBits"
            v-text="hashBit"
            :class="`pos-${index} ${hashBitComparisonClass(hashBit, index)}`"
          )
        p(v-else) Loading...
      .raw-metadata(v-else)
        highlightjs(language="json" :code="JSON.stringify(file.isccMetadata, null, 2)")
</template>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions";
@import "~bootstrap/scss/_variables";
@import "~bootstrap/scss/mixins/_border-radius";
@import "~bootstrap/scss/mixins/_breakpoints";

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

  .iscc-code {
    padding: $input-padding-y $input-padding-x;
    border: $input-border-width solid $input-border-color;
    @include border-radius($input-border-radius, 0);
  }

  .dna {
    .hash-bits {
      @include media-breakpoint-up(md) {
        width: 500px;
      }
      @include media-breakpoint-down(md) {
        flex-grow: 1;
      }

      .hash-bit {
        color: black;
        background-color: lightgray;
        display: flex;
        align-items: center;
        justify-content: center;
        float: left;
        margin: 0.4%;
        width: 5.4%;
        font-size: 1rem;
        aspect-ratio: 1 / 1;
        overflow: hidden;

        &.equal {
          background-color: green;
          color: white;
        }

        &.unequal {
          background-color: red;
          color: white;
        }

        @include media-breakpoint-down(md) {
          font-size: 0.8rem;
        }
        @include media-breakpoint-down(sm) {
          font-size: 2.75vw;
        }

        @for $i from 1 through 16 {
          $pos: calc($i * 16);

          &.pos-#{$pos} {
            clear: left;
          }
        }
      }
    }
  }
}
</style>
