<template>
  <div id="video-feed">
    <!-- space for video feeds -->
    <button
      class="uk-button uk-button-default"
      id="show-overlay-button"
      @click="showOverlay = !showOverlay"
    >
      Show Overlay
    </button>
  </div>
  <Teleport to="#video-feed">
    <div v-if="showOverlay" id="overlay">
      <div id="parent">
        <div id="video-feed-window">
          <img
            id="video-feed-placeholder"
            src="../../public/videoFeedPlaceholder.jpeg"
          />
        </div>
        <div id="stats-column">
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
            class="uk-button uk-button-default"
            id="begin-button"
            @click="begin()"
          >
            Begin
          </button>
        </div>
      </div>
      <div id="payload-buttons">
        <div id="status-bar">
          <span id="payload-status">Status: {{ status }}</span>
        </div>
        <button
          class="uk-button uk-button-default"
          id="failsafe-one"
          @click="failsafeOne()"
        >
          Failsafe 1
        </button>
        <button
          class="uk-button uk-button-default"
          id="failsafe-two"
          @click="failsafeTwo()"
        >
          Failsafe 2
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
<style scoped>
div {
  height: auto;
}
#status-bar {
  color: blue;
}
#overlay {
  position: auto;
}

#stats-column {
  float: right;
}

#show-overlay-button {
  position: relative;
  left: -10%;
}

/* #video-feed-window {
  min-height: 80%;
  width: 100%;
  overflow: auto;
} */

#video-feed-placeholder {
  position: relative;
  margin-left: 20px;
  margin-right: 20px;
  min-width: 60%;
  height: auto;
}
</style>
