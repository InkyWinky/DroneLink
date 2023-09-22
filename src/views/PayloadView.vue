<!-- TO DO:
[ ] background image
[ ] translucent overlay
[ ] put stuff in correct place 
-->
<template>
  <div
    id="video-feed"
    class="uk-height-1-1 uk-background-cover"
    data-src="../../public/videoFeedPlaceholder.jpeg"
    uk-img
  >
    <button
      class="uk-button uk-button-default"
      id="show-overlay-button"
      @click="showOverlay = !showOverlay"
    >
      Show Overlay
    </button>
  </div>
  <Teleport to="#video-feed">
    <div v-if="showOverlay" id="overlay" class="uk-height-1-1">
      <div
        id="space-filler"
        class="uk-align-left uk-width-3-4 uk-height-3-4"
      ></div>
      <div
        id="stats-column"
        class="uk-align-right uk-width-1-4 uk-height-3-4 uk-text-left"
      >
        <div id="payload-info">
          <!-- info about payload -->
          <h2>Payload Stats</h2>
          <p id="payload-height">
            Payload Height:
            {{ store?.live_data?.payload?.height }}
          </p>
          <p id="payload-vel">
            Payload Velocity:
            {{ store?.live_data?.payload?.velocity }}
          </p>
        </div>
        <div id="aircraft-info">
          <!-- info about aircraft -->
          <h2>Aircraft Stats</h2>
          <p id="alb-height">
            Albatross Ground Height:
            {{ store?.live_data?.albatross?.ground_height }}
          </p>
          <p id="alb-vel">
            Albatross Velocity:
            {{ store?.live_data?.albatross?.velocity }}
          </p>
        </div>
        <button
          class="uk-button uk-button-primary uk-align-center"
          id="begin-button"
          @click="begin()"
        >
          Begin
        </button>
      </div>
      <div id="options-bar" class="uk-align-center uk-width-1-1 uk-height-1-5">
        <span class="uk-label uk-label-warning uk-text uk-text-center">
          Status: {{ status }}
        </span>
        <button
          class="uk-button uk-button-danger"
          id="failsafe-one"
          @click="failsafeOne()"
        >
          SMERF
        </button>
        <button
          class="uk-button uk-button-danger"
          id="failsafe-two"
          @click="failsafeTwo()"
        >
          NERF
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from "vue";
import { store } from "@/store";

const status = ref("");
const showOverlay = ref(true);

function begin() {
  if (confirm("Confirm deploy payload?")) {
    console.log("Beginning deployment procedure");
    // send message to payload system to execute payload delivery
  }
}

function failsafeOne() {
  if (confirm("Confirm failsafe 1?")) {
    console.log("Executing Failsafe 1");
    // send message to payload system
  }
}

function failsafeTwo() {
  if (confirm("Confirm failsafe 2?")) {
    console.log("Executing Failsafe 2");
    // send message to payload system
  }
}
</script>
<style scoped></style>
