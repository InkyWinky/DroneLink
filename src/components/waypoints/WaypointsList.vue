<template>
  <div id="bg">
    <h2>Waypoints</h2>
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
          <i id="trashBtn" class="fa fa-trash"></i>
        </button>
      </li>
      <!-- Button for importing waypoints via csv file -->
    </ul>

    <!-- Form for adding a waypoint: -->
    <!-- Prevent default behaviour of submitting form and add waypoint instead -->
    <form @submit.prevent="addWaypt">
      <label for="longitude">Long: </label>
      <input class="coordInput" type="number" name="longitude" v-model="long" />
      <label for="latitude">Lat: </label>
      <input class="coordInput" type="number" name="latitude" v-model="lat" />
      <label for="Altitude">Alt: </label>
      <input class="coordInput" type="number" name="altitude" v-model="alt" />
      <button id="addWayptBtn"><i class="fa fa-check"></i></button>
    </form>
    <input type="file" accept=".csv" @change="readFile" />
  </div>
</template>

<script setup>
import { ref } from "vue";
// give each waypoint a unique id
let id = 0;
// Instantiate variables for coordinates
const long = ref("");
const lat = ref("");
const alt = ref("");

//And example of a waypoint object:
//Instantiat array for containing waypoints
const waypoints = ref([{ id: id++, long: 1, lat: 2, alt: 3 }]);

function addWaypt() {
  //The function addWaypt adds a waypoint to the waypoint array
  //Parameters: None
  //Inputs:None
  //Outputs: Changed waypoints array

  //Add waypoint to array
  waypoints.value.push({
    id: id++,
    long: long.value,
    lat: lat.value,
    alt: alt.value,
  });
  //Clear out input boxes after adding waypoint
  long.value = "";
  lat.value = "";
  alt.value = "";
}

function removeWaypt(waypt) {
  //The function removeWaypt removes waypoint from display and the waypoints array
  //Input: waypt to be removed
  //Output: Waypoints displayed and in array is decreased by the one to be removed
  waypoints.value = waypoints.value.filter((t) => t !== waypt);
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
    let coord = waypointsArr[i].split(", "); //Create an array called coord and split each element so that long, lat and alt are elements of the coord array
    waypoints.value.push({
      //Push each waypoint into the waypoints array
      id: id++,
      long: coord[0],
      lat: coord[1],
      alt: coord[2],
    });
  }
}
</script>
<style>
/* Background of waypoints panel */
#bg {
  width: 27%;
  height: 70%;
  background-color: white;
  padding: 1.5%;
  margin: 2%;
  border-radius: 15px;
  box-shadow: 5px 5px 5px grey;
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
}

#wayptID {
  position: absolute;
  left: 5px;
}

.coordInput {
  width: 10%;
}

#addWayptBtn {
  background-color: transparent;
  border-style: none;
}
h {
  font-family: "Aldrich", sans-serif;
}
</style>
