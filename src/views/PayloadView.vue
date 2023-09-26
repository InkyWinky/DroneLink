<!-- TO DO:
[ ] background image
[ ] translucent overlay
[ ] put stuff in correct place 
-->
<template>
  <div class="w-full bg-green-800" id="payload-body">
    <div
      id="vid-feed-large-fpv"
      v-if="!displayVisionLarge"
      class="w-full"
      @click="switchFeed()"
    >
      FPV
    </div>
    <div
      id="vid-feed-large-vision"
      v-if="displayVisionLarge"
      class="w-full"
      @click="switchFeed()"
    >
      VISION
    </div>
    <div
      id="small-vid-feed-fpv"
      class="w-1/5 h-1/4 absolute left-0 bottom-0 border-2 border-black m-2"
      v-if="displayVisionLarge"
      @click="switchFeed()"
    >
      FPV
    </div>
    <div
      id="small-vid-feed-vision"
      class="w-1/5 h-1/4 absolute left-0 bottom-0 border"
      v-if="!displayVisionLarge"
      @click="switchFeed()"
    >
      VISION
    </div>
    <div id="overlay" class="w-1/5 h-full absolute right-0" v-if="showOverlay">
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
              Albatross Ground Height:
              {{ store?.live_data?.albatross?.ground_height }}
            </p>
            <p id="alb-vel">
              Albatross Velocity:
              {{ store?.live_data?.albatross?.velocity }}
            </p>
            <p class="text-medium">STATUS: {{ status }}</p>
            <div class="w-full flex">
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
    </div>
    <div id="map-container" v-if="showMap"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { store } from "@/store";
import api from "@/api";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";

const status = ref("");
const showOverlay = ref(true);
const showMap = ref(false);
const targetCoords = ref([145.13453, -37.90984]);
const displayVisionLarge = ref(true); // boolean that determines which video feed is displayed large, and which small
// eslint-disable-next-line
onMounted(() => {
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZWxpYjAwMDMiLCJhIjoiY2t4NWV0dmpwMmM5MjJxdDk4OGtrbnU4YyJ9.YtiVLqBLZv80L9rUq-s4aw";
  new mapboxgl.Map({
    container: "map-container",
    center: targetCoords, // lng, lat
    zoom: 9,
  });
});

// eslint-disable-next-line
const targetFound = computed(() => {
  if (confirm("Confirm target found?")) {
    return true;
  } else {
    return false;
  }
});

function switchFeed() {
  displayVisionLarge.value = !displayVisionLarge.value;
  console.log("[MESSAGE] switching feeds");
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
  if (store?.state == "IDLE") {
    if (confirm("Confirm failsafe 1?")) {
      console.log("Executing Failsafe 1");
      api.executeCommand("SET_CUBE_RELAY_PIN", {
        pin_num: 0,
        pin_state: 1,
      });
    }
  } else if (store?.state == "LOWERING") {
    api.executeComand("SET_CUBE_RELAY_PIN", {
      pin_num: 0,
      pin_state: 0,
    });
  } else console.log("[ERROR] Improper State");
}

function failsafeTwo() {
  if (store?.state == "IDLE") {
    if (confirm("Confirm failsafe 2?")) {
      console.log("Executing Failsafe 2");
      api.executeCommand("SET_CUBE_RELAY_PIN", {
        pin_num: 1,
        pin_state: 1,
      });
    }
  } else if (store?.state == "LOWERING") {
    api.executeComand("SET_CUBE_RELAY_PIN", {
      pin_num: 0,
      pin_state: 0,
    });
  }
}
</script>
<style scoped>
#payload-body {
  height: calc(100vh - 70px) !important;
}
</style>
