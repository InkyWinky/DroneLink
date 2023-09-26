<!-- TO DO:
  [ ] Implement state checking !!
-->
<template>
  <div class="w-full" id="payload-body">
    <div
      v-if="displayVisionLarge.valueOf()"
      id="vid-feed-large-vision"
      class="w-full h-full bg-green-800"
    >
      VISION
    </div>
    <div
      id="vid-feed-large-fpv"
      v-else-if="!displayVisionLarge.valueOf()"
      class="w-full h-full bg-blue-800"
    >
      FPV
    </div>
    <div
      id="small-vid-feed"
      class="w-1/5 h-1/4 absolute left-0 bottom-0 border-2 border-black m-2"
      @click="switchFeed()"
    >
      <div
        id="small-vid-feed-fpv"
        v-if="displayVisionLarge.valueOf()"
        class="w-full h-full bg-blue-800"
      >
        FPV
      </div>
      <div
        id="small-vid-feed-vision"
        v-else-if="!displayVisionLarge.valueOf()"
        class="w-full h-full bg-green-800"
      >
        VISION
      </div>
    </div>
    <div
      id="overlay"
      class="w-1/5 h-full absolute top-20 right-0"
      v-if="showOverlay"
    >
      <div
        id="payload-stats"
        class="m-10 p-2 rounded bg-gray-300 border border-black opacity-80"
      >
        <div id="stats-column">
          <div id="payload-info">
            <!-- info about payload -->
            <h2 class="font-bold text-lg underline">Payload Stats</h2>
            <p id="payload-height">
              Payload Height:
              {{ store?.live_data?.payload?.height }}
            </p>
            <p id="payload-vel">
              Payload Velocity:
              {{ store?.live_data?.payload?.velocity }}
            </p>
            <!-- info about aircraft -->
            <h2 class="font-bold text-lg underline mt-8">Aircraft Stats</h2>
            <p id="alb-height">
              Ground Height:
              {{ store?.live_data?.albatross?.ground_height }}
            </p>
            <p id="alb-vel">
              Velocity:
              {{ store?.live_data?.albatross?.velocity }}
            </p>
            <p class="text-medium">STATUS: {{ status }}</p>
          </div>
          <div id="failsafe-buttons" class="w-full flex">
            <button
              class="bg-red-800 rounded-md text-white p-2 m-1 hover:bg-red-900 w-1/2"
              id="failsafe-one"
              @click="failsafeOne()"
            >
              SMERF
            </button>
            <button
              class="bg-red-800 rounded-md text-white p-2 m-1 hover:bg-red-900 w-1/2"
              id="failsafe-two"
              @click="failsafeTwo()"
            >
              NERF
            </button>
          </div>
          <div class="w-full flex" v-if="(showBegin = true)">
            <button
              class="bg-green-200 rounded-md text-black p-2 m-1 hover:bg-green-400 w-full"
              id="begin-button"
              @click="begin()"
            >
              Begin
            </button>
          </div>
        </div>
      </div>
    </div>
    <div id="map-container" v-show="showMap"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
import store from "@/store";
import api from "@/api";

const status = ref("");
const showOverlay = ref(true);
const showMap = ref(false);
const targetCoords = ref([145.13453, -37.90984]);
const displayVisionLarge = ref(false); // boolean that determines which video feed is displayed large, and which small

onMounted(() => {
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZWxpYjAwMDMiLCJhIjoiY2t4NWV0dmpwMmM5MjJxdDk4OGtrbnU4YyJ9.YtiVLqBLZv80L9rUq-s4aw";
  new mapboxgl.Map({
    container: "map-container",
    center: targetCoords.value, // lng, lat
    zoom: 9,
  });
});

function switchFeed() {
  displayVisionLarge.value = !displayVisionLarge.value;
  console.log("[MESSAGE] displayVisionLarge: " + displayVisionLarge.value);
}
/**
 * begin() initialises the payload deployment procedure, beginning by manoeuvering the drone to the chosen point on the map,
 * and then executing payload deployment
 * @param {obj} waypoint
 */
// eslint-disable-next-line
function setDeploymentLocation() {
  // get location of target (use targetCoords for now, future: targetLocation = store?.targetLocation;)
}

function begin() {
  // show localised map around target and allow user to select a place to deliver payload
  showMap.value = true;
  // implement nav command for chosen payload deployment location
  // set cube relay pin HIGH to initiate payload deployment
  if (confirm("Confirm deploy payload?")) {
    console.log("Beginning deployment procedure");
    api.executeCommand("SET_CUBE_RELAY_PIN", {
      pin_num: 0,
      pin_state: 1,
    });
  }
}

function failsafeOne() {
  if (confirm("Confirm failsafe 1?")) {
    console.log("[MESSAGE] Executing Failsafe 1");
    api.executeCommand("SET_CUBE_RELAY_PIN", {
      pin_num: 0,
      pin_state: 1,
    });
  }
  api.executeComand("SET_CUBE_RELAY_PIN", {
    pin_num: 0,
    pin_state: 0,
  });
}

function failsafeTwo() {
  if (confirm("Confirm failsafe 2?")) {
    console.log("[MESSAGE] Executing Failsafe 2");
    api.executeCommand("SET_CUBE_RELAY_PIN", {
      pin_num: 1,
      pin_state: 1,
    });
  }
  api.executeComand("SET_CUBE_RELAY_PIN", {
    pin_num: 0,
    pin_state: 0,
  });
}
</script>
<style scoped>
#payload-body {
  height: calc(100vh - 70px) !important;
}
</style>
