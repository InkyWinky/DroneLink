<template>
  <div class="home">
    <WaypointsList />
    <div id="toggleBtn"><ToggleBtn /></div>
    <div id="speedIndicator">
      <SpeedIndicator :airspeed="100" :max="150" :min="30" />
    </div>
  </div>
</template>

<script>
// @ is an alias to /src

import WaypointsList from "@/components/waypoints/WaypointsList.vue";
import ToggleBtn from "@/components/armButton/ToggleBtn.vue";
import SpeedIndicator from "@/components/speedIndicator/SpeedIndicator.vue";

// UIKit setup - should automatically propagate to the rest of the Vue app
import UIkit from "uikit";
import Icons from "uikit/dist/js/uikit-icons";
UIkit.use(Icons);

export default {
  name: "HomeView",
  components: {
    WaypointsList,
    ToggleBtn,
    SpeedIndicator,
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
  top: 80px;
  z-index: 0;
  /* Same width as waypoints list */
}
#speedIndicator {
  width: 27%;
  height: 15%;
  position: absolute;
  right: 0;
  margin: 2%;
  top: 80px;
  border-radius: 15px;
  z-index: 0;
}
</style>
