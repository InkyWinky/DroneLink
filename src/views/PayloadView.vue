<!-- TO DO:
  [ ] Implement state checking !!
  [ ] Open PLB doors button
  [ ] Load payload button
  [ ] Deployment location selector on map
  [ ] Read FPVcam footage and display instead of webcam
  [ ] Retain video feed while switching between FPV and Vision
  [ ] Print Vision footage onto other feed
-->
<template>
  <link
    href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css"
    rel="stylesheet"
  />
  <div class="w-full flex" id="payload-body">
    <div
      id="video-feed-large"
      :class="{ 'w-1/2': showMap.valueOf(), 'w-full': !showMap.valueOf() }"
    >
      <div
        v-if="displayVisionLarge.valueOf()"
        id="vid-feed-large-vision"
        class="flex flex-col w-full h-full"
      >
        VISION
        <canvas ref="vision_large" class="bg-green-800 w-full h-full"></canvas>
      </div>
      <div
        id="vid-feed-large-fpv"
        v-else-if="!displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full"
      >
        FPV
        <div
          class="w-full h-full bg-gray-800 outline outline-black flex flex-col"
        >
          <p class="text-white bg-transparent absolute text-2xl p-4">
            {{ fpv_cam_framerate.valueOf() }}
          </p>
          <canvas
            ref="fpv_large"
            class="bg-blue-500 place-self-center aspect-ratio h-full"
            :height="fpv_resolution.height"
            :width="fpv_resolution.width"
          ></canvas>
        </div>

        <!-- <video ref="FPVCamLarge" muted>Stream Unavailable</video> -->
      </div>
    </div>
    <div id="map-container" class="w-1/2" v-show="showMap.valueOf()"></div>
    <div
      id="small-vid-feed"
      class="w-1/5 h-1/4 absolute left-0 bottom-0 border-2 border-black m-2"
      @click="switchFeed()"
    >
      <div
        id="small-vid-feed-fpv"
        v-if="displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full bg-gray-200"
      >
        <p class="">FPV</p>
        <div
          class="w-full h-full bg-gray-800 outline outline-black flex flex-col"
        >
          <p class="text-white bg-transparent absolute text-2xl p-1">
            {{ fpv_cam_framerate.valueOf() }}
          </p>
          <canvas
            ref="fpv_small"
            class="bg-blue-500 aspect-video h-full"
            :height="fpv_resolution.height"
            :width="fpv_resolution.width"
          >
          </canvas>
        </div>

        <!-- <video ref="FPVCamSmall" muted>Stream Unavailable</video> -->
      </div>
      <div
        id="small-vid-feed-vision"
        v-else-if="!displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full bg-gray-200"
      >
        VISION
        <canvas ref="vision_small" class="bg-green-800 w-full h-full"></canvas>
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
import { store, fpv_cam, fpv_cam_framerate } from "@/store";
import api from "@/api";

const status = ref(null);
const showOverlay = ref(true);
const showMap = ref(false);
const targetCoords = ref([145.13453, -37.90984]); // placeholder for actual target coords
const deployCoords = ref(null);
const displayVisionLarge = ref(true); // boolean that determines which video feed is displayed large, and which small
const FPVCamLarge = ref(null);
const FPVCamSmall = ref(null);
const Map = ref(null);
// const fpv_small = document.getElementById("FPV-SMALL");
const fpv_large = ref(null);
const fpv_small = ref(null);
const vision_large = ref(null);
const vision_small = ref(null);
const fpv_resolution = reactive({ width: 1920, height: 1080 });

watch(fpv_cam, (val) => {
  if (fpv_large.value && !displayVisionLarge.value) {
    let ctx = fpv_large.value.getContext("2d");
    let image = new Image();
    image.src = val;
    // image.src = URL.createObjectURL(val);
    image.addEventListener("load", () => {
      fpv_resolution.width = image.width;
      fpv_resolution.height = image.height;
      ctx.drawImage(image, 0, 0, fpv_large.value.width, fpv_large.value.height);
    });
  } else {
    let ctx = fpv_small.value.getContext("2d");
    let image = new Image();
    // image.src = URL.createObjectURL(val);
    image.src = val;
    image.addEventListener("load", () => {
      ctx.drawImage(image, 0, 0, fpv_small.value.width, fpv_small.value.height);
    });
  }
});

onMounted(() => {
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZWxpYjAwMDMiLCJhIjoiY2t4NWV0dmpwMmM5MjJxdDk4OGtrbnU4YyJ9.YtiVLqBLZv80L9rUq-s4aw";
  Map.value = new mapboxgl.Map({
    container: "map-container",
    style: "mapbox://styles/mapbox/streets-v12", // style URL
    center: targetCoords.value, // lng, lat
    zoom: 18,
  });
  Map.value.on("click", (e) => {
    console.log("[DEPLOYMENT COORDS] " + e.lngLat);
    deployCoords.value = e.lngLat;
  });

  startFPVCapture("small");
});

function startFPVCapture(orientation) {
  if (!navigator?.mediaDevices) {
    console.log("[ERROR] Device does not have access to FPV.");
    return;
  }

  if (orientation == "large") {
    // stop small FPV feed
    if (FPVCamSmall.value != null) {
      try {
        console.log("[MESSAGE] Stopping FPVCamSmall stream");
        FPVCamSmall.value.srcObject.stream
          .getTracks()
          .forEach((track) => track.stop());
      } catch (error) {
        console.log("[ERROR] FPVCamSmall mediaStream object not found");
      }
    }
    // initiate large FPV feed
    navigator?.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        FPVCamLarge.value.srcObject = stream;
        FPVCamLarge.value.play();
        console.log("[LARGE FPV STREAM] " + stream);
      })
      .catch((error) => {
        console.log("[ERROR] FPVCam Error: " + error);
      });
  } else if (orientation == "small") {
    // stop large FPV feed
    if (FPVCamLarge.value != null) {
      try {
        console.log("[MESSAGE] Stopping FPVCamLarge stream");
        FPVCamLarge.value.srcObject.stream
          .getTracks()
          .forEach((track) => track.stop());
      } catch (error) {
        console.log("[ERROR] FPVCamLarge mediaStream object not found");
      }
    }
    // initiate small FPV feed
    navigator?.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        FPVCamSmall.value.srcObject = stream;
        FPVCamSmall.value.play();
        console.log("[SMALL FPV STREAM] " + stream);
      })
      .catch((error) => {
        console.log("[ERROR] FPVCam Error: " + error);
      });
  } else {
    console.log("[ERROR] Incorrect function call");
  }
}

function switchFeed() {
  displayVisionLarge.value = !displayVisionLarge.value;

  if (displayVisionLarge.value) {
    startFPVCapture("small");
  } else {
    startFPVCapture("large");
  }
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
