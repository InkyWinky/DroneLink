<template>
  <div class="home">
    <WaypointsList />
    <div id="toggleBtn"><ToggleBtn /></div>
  </div>
</template>

<script>
// @ is an alias to /src

import WaypointsList from "@/components/waypoints/WaypointsList.vue";
import ToggleBtn from "@/components/armButton/ToggleBtn.vue";
export default {
  name: "HomeView",
  components: {
    WaypointsList,
    ToggleBtn,
  },
};
</script>
<style>
body {
  background-color: #eeeeee;
  height: 100%;
}
div {
  height: 100%;
}
#toggleBtn {
  text-align: center;
  width: 25%;
  position: absolute;
  top: 5%;
  /* Same width as waypoints list */
}
</style>
