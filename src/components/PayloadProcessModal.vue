<template>
  <link
    href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css"
    rel="stylesheet"
  />
  <div
    class="uk-card uk-card-default uk-card-body"
    id="modal"
    style="border-radius: 15px; padding: 15px"
  >
    <div v-if="showPayloadLocSelector">
      <h1 class="title">Select deployment location of payload</h1>
      <div id="mapContainer"></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import "mapbox-gl/dist/mapbox-gl.css";
import mapboxgl from "mapbox-gl";
const showPayloadLocSelector = ref(true);
const showMap = ref(false);
const Map = ref(null);
onMounted(() => {
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
  });
});
</script>
<style scoped>
#modal {
  height: 70%;
  width: 70%;
  position: absolute;
  left: 14%;
  top: 20%;
  z-index: 9999;
  border-style: box-shadow;
}
.title {
  color: black;
  font-size: 1.2em;
  font-family: "Aldrich", sans-serif;
}
</style>
