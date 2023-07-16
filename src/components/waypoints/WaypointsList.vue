<template>
  <link
    href="https://api.mapbox.com/mapbox-gl-js/v1.12.0/mapbox-gl.css"
    rel="stylesheet"
  />
  <Transition>
    <div v-show="showMap" id="mapCon" />
  </Transition>
  <div id="bg">
    <h3>WAYPOINTS</h3>
    <div id="listWrapper" ref="listContainer">
      <ul>
        <!-- Iterate through array of waypoints and show them on list -->
        <li v-for="waypt in waypoints" :key="waypt.id">
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
      <!-- Form for adding a waypoint: -->
      <!-- Prevent default behaviour of submitting form and add waypoint instead -->
      <form @submit.prevent="addWaypt">
        <span id="plus-symbol">+</span>
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
        <button class="transparentBtn" id="addWayptBtn">
          <i class="fa fa-check white-hover" id="tick-btn"></i>
        </button>
        <button
          class="transparentBtn rightAlign"
          id="addByMapBtn"
          @click="showMap = !showMap"
          type="button"
        >
          <span class="material-symbols-outlined white-hover">
            add_location_alt
          </span>
        </button>
      </form>
    </div>
    <label for="importBtn">
      <i class="fa-solid fa-file-csv icon-btn-effect" id="importIcon"></i>
    </label>
    <input id="importBtn" type="file" accept=".csv" @change="readFile" hidden />

    <button
      class="transparentBtn"
      id="splineBtn"
      type="button"
      @click="formatWaypoints()"
    >
      <span class="material-symbols-outlined icon-btn-effect" id="splineIcon">
        timeline
      </span>
    </button>
  </div>
</template>

<script setup>
// eslint-disable-next-line no-unused-vars, prettier/prettier
import { Ref } from "vue";
import { ref, nextTick, computed } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
import { onMounted } from "vue";
import api from "../../api.js";

// give each waypoint a unique id
const showMap = ref(false);
let id = 0;
// Instantiate variables for coordinates
const long = ref("");
const lat = ref("");
const alt = ref("");
const MARKER_HEIGHT = 41;
/** @type {Ref<mapboxgl.Map>} */
const map = ref();

//And example of a waypoint object:
//Instantiat array for containing waypoints
const waypoints = ref([]);
const coordinates = computed(() =>
  waypoints.value.map(({ long, lat }) => [long, lat])
);
const listContainer = ref(null);

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

function addWaypt() {
  //The function addWaypt adds a waypoint to the waypoint array
  //Parameters: None
  //Inputs:None
  //Outputs: Changed waypoints array

  const marker = addMarkerToMap(long.value, lat.value);
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
  alt.value = "";
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
function addMarkerToMap(long, lat) {
  const marker = new mapboxgl.Marker({ offset: [0, -MARKER_HEIGHT / 2] })
    .setLngLat([long, lat])
    .addTo(map.value);
  console.log(marker);
  return marker;
}
async function testApi() {
  let coordinateData = [
    {
      id: 0,
      long: 12,
      lat: 14,
      alt: 20,
    },
    {
      id: 1,
      long: 13,
      lat: 15,
      alt: 20,
    },
    {
      id: 2,
      long: 14,
      lat: 16,
      alt: 20,
    },
  ];
  //test server
  console.log("Testing Server ...");
  const splineData = await api.fetchSpline(coordinateData);
  await api.getSpline(coordinateData, splineData);
}
testApi();
function formatWaypoints() {
  //The function formatWaypoints formats the waypoints from the gui into the format that the waypoints communication script accepts:
  //
  console.log(waypoints.value);
  let WAYPOINT_ID = 16;
  console.log(WAYPOINT_ID);
  let outputArr = [];
  for (let i = 0; i < waypoints.value.length; i++) {
    let wp = waypoints.value[i];
    let wp_obj = {
      longitude: wp.long,
      latitude: wp.lat,
      altitude: wp.alt,
      id: WAYPOINT_ID,
    };
    outputArr.push(wp_obj);
  }
  console.log(outputArr);
  return outputArr;
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
    const marker = addMarkerToMap(coord[0], coord[1]);
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
  mapboxgl.accessToken =
    "pk.eyJ1IjoiaWxpbjAwMDUiLCJhIjoiY2xlYzh3aDhhMGF3czN3bnAzYTBqMWQ0ZyJ9.P2gZdcxMsZsxg1HdvKKEJQ";
  map.value = new mapboxgl.Map({
    container: "mapCon",
    style: "mapbox://styles/mapbox/light-v9",
  });
  //Resize map to be full screen --need to find a better way to fix this problem
  map.value.on("idle", () => {
    map.value.resize();
  });
  //

  map.value.on("click", (e) => {
    //Get longitude and latitude values based on mouse click position. Had an issue where the value returned was one viewport higher than what it should be, so I adjusted it with some maths, but the marker is still placed slightly inaccurately. Need to fix.
    let container = map.value.getContainer();
    let mapHeight = container.clientHeight;
    console.log("mapHeight: " + mapHeight);
    let yPixel = e.point.y;
    let xPixel = e.point.x;
    let adjusted_yPixel = yPixel + mapHeight;
    console.log("adjusted ypixel:" + adjusted_yPixel);
    let latitude = map.value.unproject([xPixel, adjusted_yPixel]).lat;
    long.value = e.lngLat.lng;
    lat.value = latitude;
    console.log(
      JSON.stringify(e.point) + "<br />" + JSON.stringify(e.lngLat.wrap())
    );
  });

  // Add the line to the map
  map.value.on("load", drawLine);
});
</script>
<style>
/* Background of waypoints panel */
h3 {
  font-family: "Aldrich", sans-serif;
}
#bg {
  width: 26%;
  height: 72%;
  background-color: white;
  padding: 1.5%;
  margin: 2%;
  border-radius: 20px;
  box-shadow: 0px 10px 8px -3px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 200px;
  z-index: 1;
}
.white-hover:hover {
  color: white;
}
ul {
  /* Remove bullet points */
  list-style: none;
  padding: 0;
  margin: 1px;
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
  height: 85%;
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
  font-size: 3em;
  color: grey;
  z-index: 9999;
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
  z-index: 1;
}
/* Hide inbuilt mapbox footer */
.mapboxgl-ctrl-bottom-right {
  display: none;
}
#splineIcon {
  position: absolute;
  top: 95%;
  right: 15px;
  font-size: 3em;
  color: grey;
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
</style>
