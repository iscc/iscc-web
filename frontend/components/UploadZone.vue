<script setup lang="ts">
import { Dashboard } from "@uppy/vue";

import "@uppy/core/dist/style.css";
import "@uppy/dashboard/dist/style.css";

import Uppy from "@uppy/core";
import Webcam from "@uppy/webcam";
import XhrUpload from "@uppy/xhr-upload";
import UppyDashboard from "@uppy/dashboard";
import { Base64 } from "js-base64";
import { computed, onUnmounted } from "vue";

const emit = defineEmits<{
  (e: "upload-success", isccMetadata: Api.IsccMetadata): void;
}>();

const uppy = computed(() =>
  new Uppy()
    .use(UppyDashboard)
    .use(Webcam)
    .use(XhrUpload, {
      endpoint: "/api/v1/iscc",
      formData: false,
      headers: (file) => ({ "X-Upload-Filename": Base64.encode(file.name) }),
    })
    .on("upload-success", (_file, response) => {
      const metadata: Api.IsccMetadata = response.body;
      emit("upload-success", metadata);
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
