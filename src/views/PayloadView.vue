<!-- TODO
[ ] After comfirmation of target, show potential spline path for confirmation
-->
<template>
  <link
    href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css"
    rel="stylesheet"
  />

  <div class="w-full flex" id="payload-body">
    <div id="target-detected-modal" uk-modal>
      <div class="uk-modal-dialog uk-modal-body" ref="showTargetDetectedModal">
        <h2 class="uk-modal-title">Potential Target Detected</h2>
        <p>
          A potential target has been detected. Would you like to confirm this
          target?
        </p>
        <img ref="vision_potential_target" alt="target image" />
        <p class="uk-text-right">
          <button
            class="uk-button uk-button-default uk-modal-close"
            type="button"
          >
            No
          </button>
          <button class="uk-button uk-button-primary" type="button">Yes</button>
        </p>
      </div>
    </div>
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
        <div class="w-full h-full bg-green-800">
          <img ref="vision_large" class="bg-green-800 h-full w-full" />
        </div>
        <div
          id="bounding-box"
          :style="{
            height: width + '%',
            width: width + '%',
            top: y_perc - width / 2 + '%',
            right: x_perc - width / 2 + '%',
          }"
          v-show="width > 0"
        ></div>
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
      </div>
      <div
        id="small-vid-feed-vision"
        v-else-if="!displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full bg-gray-200"
      >
        VISION
        <div class="w-full h-full bg-green-800">
          <img ref="vision_small" class="bg-green-800 h-full w-full" />
        </div>
        <!-- <canvas
          ref="vision_small"
          class="bg-green-800"
          :height="vision_resolution.height"
          :width="vision_resolution.width"
        ></canvas> -->
      </div>
    </div>
    <div
      id="overlay"
      class="w-1/5 h-full absolute top-20 right-0"
      v-if="showOverlay"
    >
      <div
        id="payload-stats"
        class="m-10 p-2 rounded bg-gray-300 border border-black opacity-80 h-auto"
      >
        <div id="stats-column" class="h-auto">
          <div
            id="payload-status"
            class="m-2 p-2 rounded h-auto bg-green-500 border-black"
          >
            <p>
              <b>PAYLOAD STATUS:</b>
              {{ store?.live_data?.lifeline_status || "NOT CONNECTED" }}
            </p>
          </div>
          <div id="payload-info" class="h-auto">
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
          </div>
        </div>
        <div id="buttons" class="w-full flex h-auto">
          <div id="failsafe-btns" class="w-full flex h-auto">
            <button
              data-tooltip-target="tooltip-smerf"
              class="bg-red-800 rounded-md text-white p-2 m-1 hover:bg-red-900 w-1/2"
              id="failsafe-smerf"
              @click="smerf()"
            >
              SMERF
            </button>
            <div
              id="tooltip-smerf"
              role="tooltip"
              class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
            >
              Drop payload (Somewhat Minor Emergency Release Failsafe)
              <div class="tooltip-arrow" data-popper-arrow></div>
            </div>

            <button
              data-tooltip-target="tooltip-nerf"
              class="bg-red-800 rounded-md text-white p-2 m-1 hover:bg-red-900 w-1/2"
              id="failsafe-nerf"
              @click="nerf()"
            >
              NERF
            </button>

            <div
              id="tooltip-nerf"
              role="tooltip"
              class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
            >
              Burn rope (Nichrome Emergency Release Failsafe)
              <div class="tooltip-arrow" data-popper-arrow></div>
            </div>
          </div>
        </div>
        <div class="w-full flex h-auto" v-if="(showBegin = true)">
          <button
            class="bg-green-200 rounded-md text-black p-2 m-1 hover:bg-green-400 w-full"
            id="begin-button"
            @click="beginDeployment()"
          >
            Begin
          </button>
        </div>
        <div class="w-full flex h-auto">
          <button
            class="bg-orange-300 rounded-md text-black p-2 m-1 hover:bg-orange-500 w-full"
            id="target-found-test-btn"
            @click="confirmTarget()"
          >
            TARGET FOUND
          </button>
        </div>
        <div id="bbox-testing">
          <label for="x"> xperc</label>
          <input
            id="x"
            class="bbox-test-input"
            type="number"
            v-model="x_perc"
            style="width: 100px"
          />
          <label for="y">yperc</label>
          <input
            id="y"
            class="bbox-test-input"
            type="number"
            v-model="y_perc"
            style="width: 100px"
          />
          <label for="width"> width</label>
          <input
            id="width"
            class="bbox-test-input"
            type="number"
            v-model="width"
            style="width: 100px"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive, computed } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
import { initFlowbite } from "flowbite";
import { store, fpv_cam, fpv_cam_framerate, vision_cam } from "@/store";
import api from "@/api";
import uikit from "uikit";

const showOverlay = ref(true);
const showMap = ref(false);
const deployMarker = ref(null);
const targetCoords = ref([145.13453, -37.90984]); // placeholder for actual target coords
const deployCoords = ref(null);
const displayVisionLarge = ref(true); // boolean that determines which video feed is displayed large, and which small
const Map = ref(null);
const FPVCamLarge = ref(null);
const FPVCamSmall = ref(null);
// const fpv_small = document.getElementById("FPV-SMALL");
const fpv_large = ref(null);
const fpv_small = ref(null);
const vision_large = ref(null);
const vision_small = ref(null);
const vision_potential_target = ref(null);
const fpv_resolution = reactive({ width: 1920, height: 1080 });
//Bounding box data (all are percentages)
const x_perc = ref(50);
const y_perc = ref(50);
const width = ref(50);
const showTargetDetectedModal = ref(false);

// const vision_resolution = reactive({ width: 1920, height: 1080 });
const targetDetected = computed(() => {
  //This function turns on prompts and bounding box when target is detected and not if vision_on is false

  return store?.vision_on
    ? store?.live_data?.vision_geotag_gps || false
    : false;
});

watch(targetDetected, (newTargetData) => {
  if (newTargetData != false) {
    vision_potential_target.value.src = vision_cam;
    showTargetDetectedModal.value = true;
    console.log(newTargetData);
    targetCoords.value = [newTargetData.x, newTargetData.y]; //[LAT, LONG] I THINK
    x_perc.value = (store?.live_data?.vision_geotag_box?.x || 0) * 100;
    y_perc.value = (store?.live_data?.vision_geotag_box?.y || 0) * 100;
    width.value = (store?.live_data?.vision_geotag_box?.z || 0) * 100;
    uikit.modal("#target-detected-modal").toggle();
  }
});

watch(vision_cam, (val) => {
  if (vision_large.value && displayVisionLarge.value) {
    vision_large.value.src = val;
    // let ctx = vision_large.value.getContext("2d");
    // let image = new Image();
    // image.src = val;
    // image.src = URL.createObjectURL(val);
    // image.addEventListener("load", () => {
    //   vision_resolution.width = image.width;
    //   vision_resolution.height = image.height;
    //   console.log(vision_resolution.value);
    //   ctx.drawImage(
    //     image,
    //     0,
    //     0,
    //     vision_large.value.width,
    //     vision_large.value.height
    //   );
    // });
  } else {
    vision_small.value.src = val;
    // let ctx = vision_small.value.getContext("2d");
    // let image = new Image();
    // // image.src = URL.createObjectURL(val);
    // image.src = val;
    // image.addEventListener("load", () => {
    //   ctx.drawImage(
    //     image,
    //     0,
    //     0,
    //     vision_small.value.width,
    //     vision_small.value.height
    //   );
    // });
  }
});

watch(fpv_cam, (val) => {
  if (fpv_large.value && !displayVisionLarge.value) {
    let ctx = fpv_large.value.getContext("2d");
    let image = new Image();
    image.src = val;
    // image.src = URL.createObjectURL(val)gi;
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
  initFlowbite();
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZWxpYjAwMDMiLCJhIjoiY2t4NWV0dmpwMmM5MjJxdDk4OGtrbnU4YyJ9.YtiVLqBLZv80L9rUq-s4aw";
  Map.value = new mapboxgl.Map({
    container: "map-container",
    style: "mapbox://styles/mapbox/satellite-v9", // style URL
    center: targetCoords.value, // lng, lat
    zoom: 15,
  });
  Map.value.on("click", (e) => {
    console.log(`[DEPLOYMENT COORDS] ${e.lngLat.toArray()}`);
    deployCoords.value = e.lngLat;
    if (!deployMarker.value) {
      deployMarker.value = new mapboxgl.Marker()
        .setLngLat(e.lngLat)
        .addTo(Map.value);
    } else {
      deployMarker.value.setLngLat(e.lngLat);
    }
    console.log(`deployMarker: ${deployMarker.value}`);
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

function confirmTarget() {
  if (confirm("Confirm target?")) {
    api.executeCommand("RETURN_TO_TARGET", {});
    targetCoords.value = store?.targetCoords;
    setTimeout(() => {
      Map.value.resize();
    }, 1);
    showMap.value = true;
  }
}

/**
 * beginDeployment() begins the lifeline deployment procedure by sending the Albatross back to the confirmed target
 * and then orbiting until the pilot chooses a payload drop location
 */
function beginDeployment() {
  if (!deployMarker.value) {
    console.log("[ERROR] No deployment location set!");
    confirm("[ERROR] No deployment location set!");
    return;
  }

  if (confirm(`Confirm deploy payload at ${deployCoords.value.toArray()}?`)) {
    console.log("Beginning deployment procedure");
    api.executeCommand("DEPLOY_PAYLOAD", {
      targetCoords: targetCoords.value,
    });
  }
}

function smerf() {
  if (confirm("Confirm SMERF?")) {
    console.log("[SMERF] Executing SMERF");
    api.executeCommand("SMERF", {});
  }
}

function nerf() {
  if (confirm("Confirm failsafe 2?")) {
    console.log("[NERF] Executing NERF");
    api.executeCommand("NERF", {});
  }
}
</script>

<style scoped>
#payload-body {
  height: calc(100vh - 70px) !important;
}

#bounding-box {
  position: absolute;
  border: 5px solid red;
  z-index: 999;
}

#bbox-test-input {
  width: 100px;
}
</style>
