<!-- TO DO:
[ ] background image
[ ] translucent overlay
[ ] put stuff in correct place 
-->
<template>
  <div class="w-full bg-green-900" id="payload-body">
    <img src="videoFeedPlaceholder.jpeg" class="w-full h-full" />
    <div
      id="payload-stats"
      class="absolute w-1/5 h-5/6 right-0 top-12 m-10 p-2 rounded bg-gray-300 border border-black opacity-80"
    ></div>

    <div
      id="video-feed"
      data-src="../../public/videoFeedPlaceholder.jpeg"
      uk-img
    >
      <button id="show-overlay-button" @click="showOverlay = !showOverlay">
        Show Overlay
      </button>
    </div>
  </div>

  <Teleport to="#payload-stats" v-if="showOverlay">
    <div id="overlay">
      <div id="space-filler"></div>
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
          <button id="begin-button" @click="begin()">Begin</button>
          <span> Status: {{ status }} </span>
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
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from "vue";
import { store } from "@/store";
import api from "@/api";
import mapboxgl from "mapbox-gl";

const status = ref("");
const showOverlay = ref(true);
// const showMap = ref(false);
// const mapLocation = ref("#map-container");
const targetCoords = ref([145.13453, -37.90984]);
const map = ref("");
// const mapBig = ref(false);

/**
 * begin() initialises the payload deployment procedure, beginning by manoeuvering the drone to the chosen point on the map,
 * and then executing payload deployment
 * @param {obj} waypoint
 */

// eslint-disable-next-line
function setDeploymentLocation() {
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZWxpYjAwMDMiLCJhIjoiY2t4NWV0dmpwMmM5MjJxdDk4OGtrbnU4YyJ9.YtiVLqBLZv80L9rUq-s4aw";

  map.value = new mapboxgl.Map({
    container: "",
    center: targetCoords, // lng, lat
    zoom: 9,
  });

  // get location of target
  // use targetCoords for now
  // future: targetLocation = store?.targetLocation;
}
function begin() {
  // show localised map around target and allow user to select a place to deliver payload

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
  }
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
