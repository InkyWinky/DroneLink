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
        <img
          ref="vision_potential_target"
          alt="target image"
          class="border border-black"
        />
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
      <div id="payload-process-container" v-if="showPayloadProcess">
        <div
          class="payload-process-popup"
          style="margin-top: 4%"
          v-if="showPatientPicker"
        >
          <h1>Select patient location:</h1>
          <p class="subtitle">Click on the map on the right.</p>
          <p style="font-size: 0.8em">Go to patient located at:</p>
          <span class="accent-orange">{{
            manualPatientCoords || "None selected"
          }}</span>
        </div>
        <div v-if="showDeployLocPicker">
          <div class="payload-process-popup" style="margin-top: 4%">
            <h1>Select payload deployment location:</h1>
            <p class="subtitle">Click on the map on the right.</p>
            <p style="font-size: 0.8em">Deploy payload at ([long, lat)]:</p>
            <span class="accent-blue">{{
              deployCoords || "None selected"
            }}</span>
            <!-- <button class="popup-btn">Done</button> -->
          </div>
          <div class="payload-process-popup">
            <h1>Select altitude to deploy at:</h1>
            <input type="number" v-model="deployAlt" />
            <!-- <button class="popup-btn">Done</button> -->
          </div>
          <div class="payload-process-popup">
            <h1>Select Cardinal Direction of Approach:</h1>
            <!-- Drop down list of cardinal directions -->
            <select v-model="cardinalDir" name="direction" id="direction">
              <option value="NORTH">North</option>
              <option value="SOUTH">South</option>
              <option value="EAST">East</option>
              <option value="WEST">West</option>
            </select>
          </div>
        </div>
        <div
          id="go-btn"
          class="big-btn"
          v-if="showGoBtn"
          @click="beginDeployment()"
        >
          GO!
        </div>
        <div v-if="showDrip" style="margin-top: 5%">
          <div id="big-drip-btn" class="big-btn" @click="drip()">DRIP</div>
          <div class="big-btn shiny-pink-btn" @click="ascendRTL()">
            Ascend and RTL
          </div>
        </div>
      </div>
      <div
        v-if="displayVisionLarge.valueOf()"
        id="vid-feed-large-vision"
        class="flex flex-col w-full h-full text-white bg-black"
      >
        VISION
        <div class="flex items-center justify-center w-full h-full camera-feed">
          <div
            v-if="!has_vision_feed"
            uk-icon="icon:camera; ratio: 2"
            class="flex flex-col justify-center items-center text-white relative"
          ></div>
          <img
            v-show="has_vision_feed"
            ref="vision_large"
            class="h-[100%] w-fit"
          />
        </div>
        <div
          id="bounding-box"
          :style="{
            height: width + '%',
            width: width + '%',
            top: y_perc - width / 2 + '%',
            right: x_perc - width / 2 + '%',
          }"
          style="pointer-events: none"
          v-show="width > 0"
        ></div>
      </div>
      <div
        id="vid-feed-large-fpv"
        v-else-if="!displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full text-white bg-black"
      >
        FPV
        <div
          class="flex flex-col items-center justify-center w-full h-full bg-blue-500 outline outline-black"
        >
          <p
            class="text-white bg-transparent absolute top-16 left-2 text-2xl p-4"
          >
            {{ fpv_cam_framerate.valueOf() }}
          </p>
          <div
            v-if="!has_fpv_feed && !displayVisionLarge"
            uk-icon="icon:camera; ratio: 2"
            class="flex flex-col justify-center items-center text-white relative"
          ></div>
          <canvas
            v-show="has_fpv_feed && !displayVisionLarge"
            ref="fpv_large"
            class="bg-blue-500 aspect-video h-full"
            :height="fpv_resolution.height"
            :width="fpv_resolution.width"
          >
          </canvas>
        </div>

        <!-- <video ref="FPVCamLarge" muted>Stream Unavailable</video> -->
      </div>
    </div>
    <div id="map-container" class="w-1/2" v-show="showMap.valueOf()">
      <!-- <div>
        <img
          src="C:\Users\winky\Documents\MUAS\Mission-Management\public\planeCompass.png"
          alt="compass"
        />
      </div> -->
    </div>
    <div
      id="small-vid-feed"
      class="w-1/5 h-1/4 absolute left-0 bottom-0 border-2 border-black m-2"
      @click="switchFeed()"
    >
      <div
        id="small-vid-feed-fpv"
        v-if="displayVisionLarge.valueOf()"
        class="flex flex-col w-full h-full text-white bg-black"
      >
        <p class="">FPV</p>
        <div
          class="flex flex-col items-center justify-center w-full h-full bg-blue-500 outline outline-black"
        >
          <p
            class="text-white bg-transparent absolute top-6 left-2 text-2xl p-1"
          >
            {{ fpv_cam_framerate.valueOf() }}
          </p>
          <div
            v-if="!has_fpv_feed && displayVisionLarge"
            uk-icon="icon:camera; ratio: 2"
            class="flex flex-col justify-center items-center text-white relative"
          ></div>
          <canvas
            v-show="has_fpv_feed && displayVisionLarge"
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
        class="flex flex-col w-full h-full text-white bg-black"
      >
        VISION
        <div class="w-full h-full flex items-center justify-center camera-feed">
          <div
            v-if="!has_vision_feed && !displayVisionLarge"
            uk-icon="icon:camera; ratio: 2"
            class="flex flex-col justify-center items-center text-white relative"
          ></div>
          <img
            v-show="has_vision_feed && !displayVisionLarge"
            ref="vision_small"
            class="h-[100%] w-fit"
          />
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
      class="w-1/5 h-full absolute top-20 right-0 pointer-events-none"
      v-if="showOverlay"
    >
      <div
        id="payload-stats"
        class="m-10 p-2 rounded bg-gray-300 border border-black opacity-80 h-auto pointer-events-auto"
      >
        <div id="stats-column" class="h-auto">
          <div
            id="payload-status"
            class="m-2 p-2 rounded h-auto border-black"
            :class="{
              'bg-green-500':
                lifelineStatus?.valueOf() == 'IDLE' ||
                lifelineStatus?.valueOf() == 'LOADING' ||
                lifelineStatus?.valueOf() == 'RAISING' ||
                lifelineStatus?.valueOf() == 'LOWERING',
              'bg-green-300': lifelineStatus?.valueOf() == 'RELEASING',
              'bg-red-500': lifelineStatus?.valueOf() == 'EMERGENCY',
              'bg-gray-400': !lifelineStatus?.valueOf(),
            }"
          >
            <p>
              <b>PAYLOAD STATUS:</b>
              {{ lifelineStatus || "NOT CONNECTED" }}
            </p>
          </div>
          <div id="payload-info" class="h-auto">
            <!-- info about payload -->
            <h2 class="font-bold text-lg underline">Payload Stats</h2>
            <p id="payload-height">
              Height:
              {{ payloadHeight }} m
            </p>
            <p id="payload-vel">
              Velocity:
              {{ (store?.live_data?.lifeline_velocity || 0).toFixed(3) }} m/s
            </p>
            <!-- info about aircraft -->
            <h2 class="font-bold text-lg underline mt-8">Aircraft Stats</h2>
            <p id="alb-height">
              Ground Height:
              {{ (store?.live_data?.albatross?.ground_height || 0).toFixed(3) }}
              m
            </p>
            <p id="alb-vel">
              Velocity:
              {{ (store?.live_data?.albatross?.velocity || 0).toFixed(3) }} m/s
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
              Somewhat Minor Emergency Release Failsafe
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
              Nichrome Emergency Release Failsafe
              <div class="tooltip-arrow" data-popper-arrow></div>
            </div>
          </div>
        </div>

        <div v-if="debug_mode.valueOf()" class="w-full flex h-auto">
          <button
            class="bg-orange-300 rounded-md text-black p-2 m-1 hover:bg-orange-500 w-full"
            id="target-found-test-btn"
            @click="confirmTarget()"
          >
            MANUAL TARGET LOCATION
          </button>
        </div>
        <div v-if="debug_mode" class="w-full flex h-auto">
          <button
            class="bg-blue-300 rounded-md text-black p-2 m-1 hover:bg-blue-500 w-full"
            id="drip-btn"
            @click="drip()"
          >
            DRIP
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
import {
  store,
  fpv_cam,
  fpv_cam_framerate,
  vision_cam,
  debug_mode,
} from "@/store";
import api from "@/api";
import uikit from "uikit";
const cardinalDir = ref(false);
const showGoBtn = ref(false);
const showPayloadProcess = ref(false);
const showDeployLocPicker = ref(false);
const showPatientPicker = ref(false);
const deployAlt = ref(0);
const showOverlay = ref(true);
const showMap = ref(false);
const deployMarker = ref(null);
const patientMarker = ref(null);
const targetMarker = ref(null);
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
const has_vision_feed = ref(false);
const has_fpv_feed = ref(false);
const vision_potential_target = ref(null);
const fpv_resolution = reactive({ width: 1920, height: 1080 });
//Bounding box data (all are percentages)
const x_perc = ref(0);
const y_perc = ref(0);
const width = ref(0);
const showTargetDetectedModal = ref(true);
const manualPatientCoords = ref(null);
const showDrip = ref(false);

// const vision_resolution = reactive({ width: 1920, height: 1080 });
const visionOn = computed(() => {
  // This function turns on prompts and bounding box when target is detected and not if vision_on is false

  return store?.vision_on;
});
const geotagData = computed(() => {
  return store?.live_data?.vision_geotag_gps || 0;
});
const payloadHeight = computed(() => {
  return !store?.live_data?.sonarrange || !store?.live_data?.lifeline_distance
    ? 0
    : (
        store?.live_data?.sonarrange - store?.live_data?.lifeline_distance
      ).toFixed(3);
});

const lifelineStatus = computed(() => {
  return store?.live_data?.lifeline_status || "N/A";
});

watch(geotagData, async (newTargetData) => {
  //this triggers everytime the computed property re-evaluates even if the computed property ends up with the same value
  if (visionOn.value == true && newTargetData != 0) {
    if (
      targetCoords.value[0] != newTargetData.x &&
      targetCoords.value[1] != newTargetData.y
    ) {
      targetCoords.value = [newTargetData.x, newTargetData.y]; //[LAT, LONG] I THINK
      console.log(targetCoords.value);
    }
  }
});

watch(targetCoords, () => {
  console.log(targetCoords.value);
  if (geotagData.value != 0) {
    vision_potential_target.value.src = vision_cam.value;
    x_perc.value = (store?.live_data?.vision_geotag_box?.x || 0) * 100;
    y_perc.value = (store?.live_data?.vision_geotag_box?.y || 0) * 100;
    width.value = (store?.live_data?.vision_geotag_box?.z || 0) * 100;

    uikit.modal("#target-detected-modal").show();
    if (!targetMarker.value) {
      targetMarker.value = new mapboxgl.Marker({ color: "red" })
        .setLngLat(targetCoords.value)
        .addTo(Map);
    } else {
      targetMarker.value.setLngLat(targetCoords.value);
    }
  }
});
watch(vision_cam, (val) => {
  if (vision_large.value && displayVisionLarge.value) {
    has_vision_feed.value = true;
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
    has_vision_feed.value = true;
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
    has_fpv_feed.value = true;
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
    has_fpv_feed.value = true;
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
    console.log("x");
    console.log(`[CLICKED COORDS] ${e.lngLat.toArray()}`);
    if (showDeployLocPicker.value) {
      deployCoords.value = e.lngLat;
      if (!deployMarker.value) {
        deployMarker.value = new mapboxgl.Marker()
          .setLngLat(e.lngLat)
          .addTo(Map.value);
      } else {
        deployMarker.value.setLngLat(e.lngLat);
      }
    } else if (showPatientPicker.value) {
      manualPatientCoords.value = e.lngLat;
      if (!patientMarker.value) {
        patientMarker.value = new mapboxgl.Marker({ color: "orange" })
          .setLngLat(e.lngLat)
          .addTo(Map.value);
      } else {
        patientMarker.value.setLngLat(e.lngLat);
      }
    }
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
  console.log(
    "[MESSAGE] Large display now showing " + displayVisionLarge.value
      ? "Vision"
      : "FPV"
  );
}

function confirmTarget() {
  if (
    confirm(
      "Add Manual Target Location. Do not press this button if the drone is not in CRUISE mode. \n\nConfirm?"
    )
  ) {
    showMap.value = true;
    showPayloadProcess.value = true;
    showPatientPicker.value = true;
    showGoBtn.value = true;
    Map.value.flyTo({
      center: [store?.live_data?.lng, store?.live_data?.lat],
      zoom: 13,
    });
    targetCoords.value = store?.targetCoords;
    setTimeout(() => {
      Map.value.resize();
    }, 1000);
  }
}
/**
 * beginDeployment() begins the lifeline deployment procedure by sending the Albatross back to the confirmed target
 * and then orbiting until the pilot chooses a payload drop location
 */
function beginDeployment() {
  if (showDeployLocPicker.value) {
    if (!deployMarker.value) {
      console.log("[ERROR] No deployment location set!");
      confirm("[ERROR] No deployment location set!");
      return;
    }
    if (
      confirm(
        `Are you sure you want to deploy payload at\n ${deployCoords.value.toArray()}?`
      )
    ) {
      console.log("Beginning deployment procedure");

      showPatientPicker.value = false;
      showDeployLocPicker.value = false;
      showGoBtn.value = false;
      showDrip.value = true;
      //Travel to payload drop location
      api.executeCommand("DROP_LOCATION", {
        dropoff_coordinates: {
          lat: deployCoords.value.lat,
          long: deployCoords.value.lng,
          alt: deployAlt.value, // This alt is dependant on user input
        },
        cruise_alt: store?.settings?.default_alt,
        transition_alt: store?.settings?.takeoff_alt,
        cardinal_approach: cardinalDir.value,
      });
    }
  } else if (showPatientPicker.value) {
    showDeployLocPicker.value = true;
    showPatientPicker.value = false;

    if (!patientMarker.value) {
      console.log("[ERROR] No patient location set!");
      confirm("[ERROR] No patient location set!");
      return;
    }
    if (
      confirm(
        `Are you sure you want to go to patient at\n ${patientMarker.value
          .getLngLat()
          .toArray()}?`
      )
    ) {
      //Travel to patient
      console.log(manualPatientCoords.value);
      api.executeCommand("PATIENT_LOCATION", {
        patient_location: {
          lat: manualPatientCoords.value.lat,
          long: manualPatientCoords.value.lng,
          alt: store?.settings?.default_alt,
        },
      });
      console.log("Beginning flight to patient procedure");
    }
  }
}

function smerf() {
  if (confirm(`SMERF will deploy the payoad immediately.\n\nConfirm?`)) {
    console.log("[MESSAGE] Executing SMERF");
    api.executeCommand("SMERF", {});
  }
}

function nerf() {
  if (confirm("NERF will burn the rope holding the payload.\n\nConfirm?")) {
    console.log("[MESSAGE] Executing NERF");
    api.executeCommand("NERF", {});
  }
}

function drip() {
  if (confirm("DRIP will deploy the payload.\n\nConfirm?")) {
    console.log("[MESSAGE] Executing DRIP");
    api.executeCommand("DRIP", {});
  }
}
function ascendRTL() {
  if (
    confirm(
      "Ascend and RTL will ascend the aircraft to the default altitude and then return to home. Do not press this if the plane is not in VTOL mode.\n\nConfirm?"
    )
  ) {
    console.log("[MESSAGE] Executing Ascend and RTL");
    api.executeCommand("ASCEND_AND_RTL", {
      dropoff_coordinates: {
        lat: deployCoords.value.lat,
        long: deployCoords.value.lng,
        alt: deployAlt.value, // This alt is dependant on user input
      },
      cruise_alt: store?.settings?.default_alt,
      transition_alt: store?.settings?.takeoff_alt,
      cardinal_direction: cardinalDir.value,
    });
  }
}

const droneMarker = ref();
const droneLocation = computed(() => [
  store?.live_data?.lng,
  store?.live_data?.lat,
]);
watch(droneLocation, (val) => {
  if (val[0] && val[1]) {
    updateDroneMarker(val[0], val[1]);
  }
});

function updateDroneMarker(latitude, longitude) {
  if (droneMarker.value) {
    droneMarker.value.setLngLat([latitude, longitude]).addTo(Map.value);
  } else {
    // Add drone marker to map
    var el = document.createElement("div");
    el.className = "marker droneMarker";
    el.innerHTML = "<span><b></b></span>";
    const marker = new mapboxgl.Marker(el) //({ offset: [0, -MARKER_HEIGHT / 2] })
      .setLngLat([latitude, longitude])
      .addTo(Map.value);
    droneMarker.value = marker;
  }
}
</script>

<style scoped>
.payload-process-popup {
  height: 20%;
  width: 75%;
  margin: 2%;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  z-index: 999;
  text-align: left;
  border-style: box-shadow;
}

.payload-process-popup:hover {
  transform: scale(1.01);
  transition: transform 0.1s ease-out;
}

h1 {
  font-family: "Aldrich", sans-serif;
}

#payload-body {
  height: calc(100vh - 70px) !important;
}

#bounding-box {
  position: absolute;
  border: 5px solid red;
  z-index: 999;
}

#payload-process-container {
  background-color: none;
  width: 50%;
  position: absolute;
  left: 0;
  z-index: 9999;
}

#bbox-test-input {
  width: 100px;
}

.subtitle {
  font-size: 0.8em;
  font-family: "Open Sans", sans-serif;
}

.popup-btn {
  background-color: #368bac;
  border: none;
  color: white;
  padding: 10px;
  border-radius: 5px;
  float: right;
}

.accent-blue {
  color: #368bac;
  font-weight: bold;
}

.accent-orange {
  color: #f08000;
  font-weight: bold;
}

#go-btn {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
}

#big-drip-btn {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
}

.big-btn {
  color: white;

  width: 75%;
  padding: 20px;
  border-radius: 10px;
  margin: 2%;
  border-style: box-shadow;
  font-style: bold;
  font-size: 1.2em;
}

#go-btn:hover {
  transform: scale(1.05);
  transition: transform 0.1s ease-out;
}

.camera-feed {
  background-color: #3e4663;
}
.marker.droneMarker {
  width: 0;
  height: 0;
  z-index: 99;
}
.marker.droneMarker b {
  transform: rotateZ(135deg);
}
.marker.droneMarker span {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  width: 15px;
  height: 15px;
  color: #000000;
  background: rgb(255, 25, 25);
  border: solid 2px;
  /* border-radius: 0 70% 70%; */
  /* box-shadow: 0 0 2px #000; */
  cursor: pointer;
  transform-origin: 5px 8px;
  /* transform: rotateZ(-135deg); */
}
</style>
