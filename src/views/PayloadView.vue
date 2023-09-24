<!-- TO DO:
[ ] background image
[ ] translucent overlay
[ ] put stuff in correct place 
-->
<template>
  <div id="video-feed" data-src="../../public/videoFeedPlaceholder.jpeg" uk-img>
    <button id="show-overlay-button" @click="showOverlay = !showOverlay">
      Show Overlay
    </button>
  </div>
  <Teleport to="#video-feed" v-if="payloadInit">
    <!-- <div v-if="showOverlay" id="overlay">
      <div id="space-filler"></div>
      <div id="stats-column">
        <div id="payload-info">
          info about payload
          <h2>Payload Stats</h2>
          <p id="payload-height">
            Payload Height:
            {{ store?.live_data?.payload?.height }}
          </p>
          <p id="payload-vel">
            Payload Velocity:
            {{ store?.live_data?.payload?.velocity }}
          </p>
          info about aircraft
          <h2>Aircraft Stats</h2>
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
          <button id="failsafe-one" @click="failsafeOne()">SMERF</button>
          <button id="failsafe-two" @click="failsafeTwo()">NERF</button>
        </div>
        <div id="aircraft-info">
        </div>
      </div>
    </div> -->
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { store } from "@/store";
import api from "@/api";
import mapboxgl from "mapbox-gl";

const status = ref("");
const payloadInit = ref(false);
const showOverlay = ref(true);
// const showMap = ref(false);
// const mapLocation = ref("#map-container");
const targetCoords = ref([145.13453, -37.90984]);
const map = ref("");
const mapBig = ref(false);

onMounted(() => {});
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
<style scoped></style>
