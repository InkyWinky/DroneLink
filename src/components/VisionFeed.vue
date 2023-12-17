<template>
  <div
    class="uk-card uk-card-default uk-card-body p-2"
    style="border-radius: 15px"
  >
    <router-link
      to="/payload"
      class="w-full h-full items-center justify-center"
    >
      <h3>VISION FEED</h3>
    </router-link>

    <div class="bg-gray-500 rounded-md border border-black" style="height: 90%">
      <div
        v-if="!has_feed"
        uk-icon="icon:camera; ratio: 2"
        class="flex flex-col justify-center items-center text-white relative"
      ></div>
      <img v-show="has_feed" ref="vision_feed" class="h-full w-full" />
    </div>
  </div>
</template>
<script setup>
import { ref, watch } from "vue";
import { vision_cam } from "../store";
const vision_feed = ref(null);
const has_feed = ref(false);

watch(vision_cam, (val) => {
  if (vision_cam.value) {
    has_feed.value = true;
    vision_feed.value.src = val;
  }
});
</script>
<style scoped>
div {
  height: 100%;
}
</style>
