<template>
  <div class="home">
    <WaypointsList />
    <div id="toggleBtn"><ToggleBtn /></div>
    <div id="speedIndicator">
      <SpeedIndicator :airspeed="0" :max="150" :min="0" />
    </div>
    <div id="notePad">
      <NotePad />
    </div>
    <div id="batteryStats">
      <BatteryStatistics />
    </div>
  </div>
</template>

<script>
// @ is an alias to /src

import WaypointsList from "@/components/waypoints/WaypointsList.vue";
import ToggleBtn from "@/components/armButton/ToggleBtn.vue";
import SpeedIndicator from "@/components/speedIndicator/SpeedIndicator.vue";
import NotePad from "@/components/notePad/NotePad.vue";
import BatteryStatistics from "@/components/batteryStats/BatteryStatistics.vue";

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
    NotePad,
    BatteryStatistics,
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
  width: 29%;
  height: 15%;
  position: absolute;
  right: 0;
  margin: 2%;
  top: 70px;
  border-radius: 15px;
  z-index: 0;
}

#notePad {
  position: absolute;
  left: 35.5%;
  width: 29%;
  height: 60%;
  top: 110px;
  z-index: 0;
}

#batteryStats {
  position: absolute;
  width: 29%;
  left: 35.5%;
  bottom: 30px;
  height: 25%;
}
</style>
