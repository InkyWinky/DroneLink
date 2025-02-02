<template>
  <link
    href="https://api.mapbox.com/mapbox-gl-js/v1.12.0/mapbox-gl.css"
    rel="stylesheet"
  />
  <Transition>
    <div v-show="showMap" id="mapCon" />
  </Transition>
  <div id="bg">
    <h3>PATH PLANNER</h3>
    <button
      class="rightAlign"
      id="addByMapBtn"
      @click="toggleMap"
      type="button"
    >
      <i
        class="fa-solid fa-map-location-dot icon-btn-effect"
        style="color: lightslategray"
      ></i>
    </button>
    <div
      id="listWrapper"
      ref="listContainer"
      class="flex flex-col outline outline-1 rounded-md my-1 overflow-hidden"
    >
      <ul class="h-full overflow-y-auto">
        <!-- Iterate through array of waypoints and show them on list -->
        <li
          class="cursor-pointer"
          v-for="waypt in waypoints"
          :key="waypt.id"
          @click="zoomToWaypoint(waypt)"
        >
          <span id="wayptID">{{ waypt.id }}</span>
          <span> Long:</span>
          {{ waypt.long }}
          <span> Lat:</span>
          {{ waypt.lat }}
          <span> Alt:</span>
          {{ waypt.alt }}
          <button id="removeWayptBtn" @click="removeWaypt(waypt)">
            <i id="trashBtn" class="fa fa-trash white-hover"></i>
          </button>
        </li>
        <!-- Button for importing waypoints via csv file -->
      </ul>
      <div
        class="border-y-2 text-sm flex flex-col md:flex-row justify-between items-center px-4"
      >
        <p class="font-bold">Actions</p>
        <button @click="clearWaypts">CLEAR</button>
        <!-- <button @click="">ANOTHER ACTION</button> -->
      </div>
      <!-- Form for adding a waypoint: -->
      <!-- Prevent default behaviour of submitting form and add waypoint instead -->
      <form @submit.prevent="addWaypt">
        <div>
          <button class="transparentBtn" id="addWayptBtn">
            <span class="white-hover" id="plus-symbol">+</span>
          </button>
          <label for="longitude">Long: </label>
          <input
            class="coordInput"
            type="number"
            name="longitude"
            step="any"
            v-model="long"
          />
          <label for="latitude">Lat: </label>
          <input
            class="coordInput"
            type="number"
            step="any"
            name="latitude"
            v-model="lat"
          />
          <label for="Altitude">Alt: </label>
          <input
            class="coordInput"
            type="number"
            step="any"
            name="altitude"
            v-model="alt"
          />
        </div>
      </form>
    </div>
    <button
      class="flex flex-row w-full justify-center items-center p-1 rounded-md text-xs divide-black divide-x-2 shiny-pink-btn"
      data-tooltip-target="tooltip-location"
      @click="addCurrentLocationWaypt"
    >
      <p class="px-1 font-bold">Lat: {{ store?.live_data?.lat || "N/A" }}</p>
      <p class="px-1 font-bold">Long: {{ store?.live_data?.lng || "N/A" }}</p>
      <p class="px-1 font-bold">
        Alt:
        {{ store?.live_data?.alt ? store?.live_data?.alt.toFixed(2) : "N/A" }}
      </p>
    </button>
    <div
      id="tooltip-location"
      role="tooltip"
      class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
    >
      Add Current GPS Location as Waypoint
      <div class="tooltip-arrow" data-popper-arrow></div>
    </div>
    <label for="importBtn">
      <i
        class="fa-solid fa-file-csv icon-btn-effect"
        data-tooltip-target="tooltip-csv"
        id="importIcon"
      ></i>
    </label>
    <input id="importBtn" type="file" accept=".csv" @change="readFile" hidden />
    <div
      id="tooltip-csv"
      role="tooltip"
      class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
    >
      Import waypoints as csv file
      <div class="tooltip-arrow" data-popper-arrow></div>
    </div>

    <button
      data-tooltip-target="tooltip-spline"
      class="transparentBtn"
      id="splineBtn"
      type="button"
      @click="formatWaypoints()"
    >
      <span class="material-symbols-outlined icon-btn-effect" id="splineIcon">
        timeline
      </span>
    </button>
    <div
      id="tooltip-spline"
      role="tooltip"
      class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
    >
      Spline search path given boundary coordinates
      <div class="tooltip-arrow" data-popper-arrow></div>
    </div>
    <button
      data-tooltip-target="tooltip-test"
      class="transparentBtn"
      id="testBtn"
      type="button"
      @click="testWaypoints()"
    >
      <i
        class="fa-solid fa-plane icon-btn-effect"
        style="color: lightslategray"
      ></i>
    </button>
    <!-- Tooltip for testing button -->
    <div
      id="tooltip-test"
      role="tooltip"
      class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
    >
      Fly splined path to waypoints
      <div class="tooltip-arrow" data-popper-arrow></div>
    </div>
  </div>
</template>

<script setup>
// eslint-disable-next-line no-unused-vars, prettier/prettier
// import { Ref } from "vue";
import { ref, nextTick, computed, watch } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
import { onMounted } from "vue";
import api from "../../api.js";
import { store } from "@/store";
import { initFlowbite } from "flowbite";

// give each waypoint a unique id
const showMap = ref(false);
let id = 0;
// Instantiate variables for coordinates
const long = ref("");
const lat = ref("");
const alt = ref(store?.settings.default_alt.toString() || "20");
// const MARKER_HEIGHT = 41;
// /** @type {Ref<mapboxgl.Map>} */
const map = ref();

//And example of a waypoint object:
//Instantiat array for containing waypoints
const waypoints = ref([]);
const coordinates = computed(() =>
  waypoints.value.map(({ long, lat }) => [long, lat])
);
const listContainer = ref(null);
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
    droneMarker.value.setLngLat([latitude, longitude]).addTo(map.value);
  } else {
    // Add drone marker to map
    var el = document.createElement("div");
    el.className = "marker droneMarker";
    el.innerHTML = "<span><b></b></span>";
    const marker = new mapboxgl.Marker(el) //({ offset: [0, -MARKER_HEIGHT / 2] })
      .setLngLat([latitude, longitude])
      .addTo(map.value);
    droneMarker.value = marker;
  }
}

function toggleMap() {
  showMap.value = !showMap.value;
  setTimeout(() => {
    map.value.resize();
  }, 1);
}
function scrollBottom() {
  listContainer.value.scrollTop = listContainer.value.scrollHeight;
}
// Create a GeoJSON feature collection for the line
function lineFeature(coordinates) {
  return {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates,
        },
      },
    ],
  };
}

function drawLine() {
  map.value.addLayer({
    id: "route",
    type: "line",
    source: {
      type: "geojson",
      data: lineFeature(coordinates.value),
    },
    layout: {
      "line-join": "round",
      "line-cap": "round",
    },
    paint: {
      "line-color": "#888",
      "line-width": 8,
    },
  });
}

// Update the line when the list of waypoints changes
function updateLine(coords) {
  map.value.getSource("route").setData(lineFeature(coords));
}

function addCurrentLocationWaypt() {
  // This function adds the current GPS Location of the drone as a waypoint.
  long.value = store?.live_data?.lng;
  lat.value = store?.live_data?.lat;
  alt.value = store?.settings.default_alt.toString() || "20";
  addWaypt();
}

function clearWaypts() {
  // Clears all waypoints from list and map
  for (let waypoint of waypoints.value) {
    removeWaypt(waypoint);
  }
  id = 0;
}

function addWaypt() {
  //The function addWaypt adds a waypoint to the waypoint array
  //Parameters: None
  //Inputs:None
  //Outputs: Changed waypoints array
  const marker = addMarkerToMap(long.value, lat.value, id);
  //Add waypoint to array
  waypoints.value.push({
    id: id++,
    long: parseFloat(long.value).toFixed(8),
    lat: parseFloat(lat.value).toFixed(8),
    alt: alt.value,
    marker,
  });
  //Clear out input boxes after adding waypoint
  long.value = "";
  lat.value = "";
  alt.value = store?.settings.default_alt.toString() || "20";
  updateLine(coordinates.value);
  nextTick(() => {
    scrollBottom();
  });
}

function removeWaypt(waypt) {
  //The function removeWaypt removes waypoint from display and the waypoints array
  //Input: waypt to be removed
  //Output: Waypoints displayed and in array is decreased by the one to be removed
  waypoints.value?.find((t) => t === waypt)?.marker?.remove();
  waypoints.value = waypoints.value.filter((t) => t !== waypt);
  updateLine(coordinates.value);
}
function addMarkerToMap(long, lat, id) {
  var el = document.createElement("div");
  el.className = "marker";
  el.innerHTML = "<span><b>" + id + "</b></span>";
  const marker = new mapboxgl.Marker(el) //({ offset: [0, -MARKER_HEIGHT / 2] })
    .setLngLat([long, lat])
    .addTo(map.value);
  console.log(marker);
  return marker;
}
function zoomToWaypoint(waypt) {
  let longLat = [
    waypoints.value?.find((t) => t === waypt).long,
    waypoints.value?.find((t) => t === waypt).lat,
  ];

  map.value.flyTo({ center: longLat, zoom: 17 });
}

// async function testApi() {
// let coordinateData = [
//   {
//     id: 0,
//     long: 12,
//     lat: 14,
//     alt: 20,
//   },
//   {
//     id: 1,
//     long: 13,
//     lat: 15,
//     alt: 20,
//   },
//   {
//     id: 2,
//     long: 14,
//     lat: 16,
//     alt: 20,
//   },
// ];
// console.log("Testing Server ...");
// const splineData = await api.fetchSpline(coordinateData);
// const commandResult = await api.executeCommand(
//   "OVERRIDE_FLIGHTPLANNER",
//   coordinateData
// );
// console.log("commandResult", commandResult);
// await api.getSpline(coordinateData, splineData);
// }
// testApi();
//TODO: add drop down in gui to change the waypoint ids and input takeoff altitude

async function formatWaypoints() {
  //The function formatWaypoints formats the waypoints from the gui into the format that the waypoints communication script accepts:
  //
  const takeoff_alt = store?.settings?.takeoff_alt || 20;
  console.log(waypoints.value);
  let WAYPOINT_ID = store?.settings?.waypoint_type || 16;
  console.log(WAYPOINT_ID);
  let outputArr = [];
  for (let i = 0; i < waypoints.value.length; i++) {
    let wp = waypoints.value[i];
    let wp_obj = {
      long: parseFloat(wp.long),
      lat: parseFloat(wp.lat),
      alt: parseFloat(wp.alt),
      id: WAYPOINT_ID,
    };
    outputArr.push(wp_obj);
  }
  const commandResult = await api.executeCommand("OVERRIDE_FLIGHTPLANNER", {
    waypoints: outputArr,
    takeoff_alt: takeoff_alt,
    cruise_alt: store?.settings?.default_alt,
    vtol_transition_mode: store?.settings?.vtol_transition_mode,
    drone_location: { lat: store?.live_data?.lat, long: store?.live_data?.lng },
    min_turn_radius: store?.settings?.min_turn_radius,
  });

  console.log("commandResult", commandResult);
  console.log("outputArr", outputArr);
  console.log("takeoffalt", takeoff_alt);
  console.log("vtol_t:", store?.settings?.vtol_transition_mode);
  return outputArr;
}
async function testWaypoints() {
  const takeoff_alt = store?.settings?.takeoff_alt || 20;
  console.log(waypoints.value);
  let WAYPOINT_ID = store?.settings?.waypoint_type || 16;
  console.log(WAYPOINT_ID);
  let outputArr = [];
  for (let i = 0; i < waypoints.value.length; i++) {
    let wp = waypoints.value[i];
    let wp_obj = {
      long: parseFloat(wp.long),
      lat: parseFloat(wp.lat),
      alt: parseFloat(wp.alt),
      id: WAYPOINT_ID,
    };
    outputArr.push(wp_obj);
  }
  const commandResult = await api.executeCommand("OVERRIDE", {
    waypoints: outputArr,
    takeoff_alt: takeoff_alt,
    vtol_transition_mode: store?.settings?.vtol_transition_mode,
  });
  console.log("commandResult", commandResult);
}
function readFile(formInput) {
  //The function readFile reads the waypoiants from the csv file chosen in the input form and turns it into text
  //Input: formInput is the file that was selected when you click "import waypoints from csv" button
  //Output: The text result is fed into the addWaypointsFromTxt function

  //Get the file from <input> element which will be the first file as only one file is uploaded
  let file = formInput.target.files[0];
  //Create a new FileReader
  let reader = new FileReader();
  //After the reader has loaded, input the text result into the addWaypointsFromTxt function
  reader.onload = (e) => addWaypointsFromTxt(e.currentTarget.result);
  reader.readAsText(file);
}

function addWaypointsFromTxt(csvText) {
  //The function addWaypointsFromTxt reads the input text and adds the waypoints to the waypoints array /to be displayed
  //Input: csvText is a string in the format "long, lat, alt\r\n, long, lat, alt\r\r\n..."
  //Output: The waypoints from the input string are pushed into the 'waypoints' array variable to be displayed

  let waypointsArr = csvText.split("\r\n"); //Split the text so that each waypoint is an element in an array
  for (let i = 0; i < waypointsArr.length; i++) {
    //Iterate through the resulting array
    let coord = waypointsArr[i].split(","); //Create an array called coord and split each element so that long, lat and alt are elements of the coord array
    const marker = addMarkerToMap(coord[0], coord[1], i);
    waypoints.value.push({
      //Push each waypoint into the waypoints array
      id: id++,
      long: coord[0],
      lat: coord[1],
      alt: coord[2],
      marker,
    });
  }
  map.value.flyTo({
    center: [waypoints.value[0].long, waypoints.value[0].lat],
    zoom: 15,
  }); //Center map to first waypoint in list
  updateLine(coordinates.value);
  nextTick(() => {
    //Keep scroll at bottom of list
    scrollBottom();
  });
}

onMounted(() => {
  initFlowbite();
  let droneLat = store?.live_data?.lat;
  if (droneLat == null) {
    droneLat = -37.9616111291979; //Default value
  }
  let droneLong = store?.live_data?.long;
  if (droneLong == null) {
    droneLong = 145.24602266283097;
  }
  mapboxgl.accessToken =
    "pk.eyJ1IjoiaWxpbjAwMDUiLCJhIjoiY2xlYzh3aDhhMGF3czN3bnAzYTBqMWQ0ZyJ9.P2gZdcxMsZsxg1HdvKKEJQ";
  map.value = new mapboxgl.Map({
    container: "mapCon",
    style: "mapbox://styles/mapbox/satellite-v9",
    //Default center at melbourne Police Paddocks Dandenont
    center: [droneLong, droneLat],
    zoom: 17,
  });
  //Resize map to be full screen --need to find a better way to fix this problem
  map.value.on("idle", () => {
    map.value.resize();
  });
  //

  map.value.on("click", (e) => {
    //Get longitude and latitude values based on mouse click position. Had an issue where the value returned was one viewport higher than what it should be, so I adjusted it with some maths, but the marker is still placed slightly inaccurately. Need to fix.
    // let container = map.value.getContainer();
    // let mapHeight = container.clientHeight;
    // console.log("mapHeight: " + mapHeight);
    let yPixel = e.point.y;
    let xPixel = e.point.x;
    let adjusted_yPixel = yPixel;
    // console.log("adjusted ypixel:" + adjusted_yPixel);
    let latitude = map.value.unproject([xPixel, adjusted_yPixel]).lat;
    long.value = e.lngLat.lng;
    lat.value = latitude;
    addWaypt();
    long.value = e.lngLat.lng;
    lat.value = latitude;
    console.log(
      JSON.stringify(e.point) + "<br />" + JSON.stringify(e.lngLat.wrap())
    );
  });

  // Add the line to the map
  map.value.on("load", drawLine);
  // disable map rotation using right click + drag
  map.value.dragRotate.disable();
  // disable map rotation using touch rotation gesture
  map.value.touchZoomRotate.disableRotation();
});
</script>

<style scoped>
/* Background of waypoints panel */
h3 {
  font-family: "Aldrich", sans-serif;
}
ul {
  /* Remove bullet points */
  list-style: none;
  padding: 0;
  margin: 1px;
  font-size: 0.8em;
}
li {
  background-color: #eeeeee;
  border-radius: 5px;
  padding: 1.5%;
  position: relative;
  margin: 2%;
  padding-left: 25px;
}
input {
  border-style: none;
}
form {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
  border-radius: 5px;
  padding: 1.5%;
  position: relative;
  margin: 2%;
}

li:hover {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
}
</style>
<style>
#bg {
  width: 30%;
  height: 70%;
  background-color: white;
  padding: 1.5%;
  border-radius: 20px;
  box-shadow: 0px 10px 8px -3px rgba(0, 0, 0, 0.1);
  z-index: 3;
  position: absolute;
  top: 26%;
  left: 3%;
}
.white-hover:hover {
  color: white;
}

#removeWayptBtn {
  background-color: transparent;
  border-style: none;
  display: none;
  position: absolute;
  right: 1em;
  padding: 0;
}

li:hover #removeWayptBtn,
#removeWayptBtn:hover {
  display: inline-block;
}
span {
  font-weight: bold;
  font-size: 0.8em;
}

#wayptID {
  position: absolute;
  left: 5px;
}

.coordInput {
  width: 10%;
  font-size: 0.8em;
}
label {
  font-size: 0.8em;
  margin: 5px;
}
#tick-btn {
  font-size: 1.5em;
  position: absolute;
  right: 35px;
  top: 8px;
}
.transparentBtn {
  background-color: transparent;
  border-style: none;
}

#listWrapper {
  height: 78%;
  overflow: auto;
}
/* #importBtn {
  position: absolute;
  bottom: 15px;
  left: 15px;
} */
#importIcon {
  position: absolute;
  bottom: 15px;
  left: 15px;
  font-size: 2.5em;
  color: lightslategrey;
  z-index: 0.99;
}

#testBtn {
  position: absolute;
  bottom: 5px;
  right: 80px;
  font-size: 2em;
  color: lightslategrey;
  z-index: 0.99;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
#mapCon {
  height: 100%;
  position: relative;
  overflow: hidden;
  z-index: 2;
}
/* Hide inbuilt mapbox footer */
.mapboxgl-ctrl-bottom-right {
  display: none;
}
#splineBtn {
  position: absolute;
  bottom: 20px;
  right: 10px;
  font-size: 2em;
  color: lightslategray;
  padding: 0;
  height: 40px;
}

/* remove number input arrows */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
/* .mapboxgl-canvas {
  height: 100vh !important;
} */
/* .mapboxgl-canvas-container {
  height: 100vh !important;
  width: 100vw !important;
} */
.mapboxgl-marker {
  margin: 0 !important;
  height: 41px !important;
}

/* Add location icon */
.material-symbols-outlined {
  font-variation-settings: "FILL" 1, "wght" 400, "GRAD" 0, "opsz" 48;
  position: absolute;
  right: 10px;
  top: 8px;
  font-size: 1.5em;
}

#plus-symbol {
  left: 15px;
  position: absolute;
  font-size: 2em;
  font-weight: lighter;
  top: -5px;
}
.icon-btn-effect:hover {
  color: #2c3e50 !important;
  transform: scale(1.1); /* increase size by 20% */
  transition: transform 0.1s ease-out; /* add a smooth transition */
}
.coordInput {
  height: 50%;
  width: 15%;
  padding: 2px;
  border-radius: 2px;
  font-size: 0.8em;
}
#addByMapBtn {
  position: absolute;
  top: 7px;
  right: 15px;
  font-size: 1.5em;
  color: lightslategray;
  padding: 0;
  height: 40px;
}
.marker {
  width: 0;
  height: 0;
}
.marker span {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  width: 30px;
  height: 30px;
  color: #fff;
  background: linear-gradient(0.4turn, #79d9ff, #9198e5);
  border: solid 2px;
  border-radius: 0 70% 70%;
  box-shadow: 0 0 2px #000;
  cursor: pointer;
  transform-origin: 5px 8px;
  transform: rotateZ(-135deg);
  border: none;
}
.marker b {
  transform: rotateZ(135deg);
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

<style>
.shiny-pink-btn {
  background: linear-gradient(0.25turn, #dab0f0, #9198e5);
}
.shiny-pink-btn:hover {
  animation-name: shine;
  animation-duration: 300ms;
  animation-fill-mode: forwards;
}
@keyframes shine {
  0% {
    background: linear-gradient(0.25turn, #e9cafa, #dab0f0, #9198e5, #9198e5);
  }

  25% {
    background: linear-gradient(
      0.25turn,
      #e9cafa,
      #dab0f0,
      #dab0f0,
      #9198e5,
      #9198e5
    );
  }

  50% {
    background: linear-gradient(
      0.25turn,
      #e9cafa,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #9198e5
    );
  }
  50% {
    background: linear-gradient(
      0.25turn,
      #e9cafa,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #9198e5
    );
  }
  75% {
    background: linear-gradient(
      0.25turn,
      #e9cafa,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #bfa7ec
    );
  }
  100% {
    background: linear-gradient(
      0.25turn,
      #e9cafa,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #dab0f0,
      #bfa7ec
    );
  }
}
</style>
