<template>
  <PathPlanner />
  <!-- Add UI kit tab -->

  <div id="toggleBtn"><ToggleBtn /></div>
  <div id="speedIndicator">
    <SpeedIndicator
      :airspeed="Number(store?.live_data?.airspeed?.toFixed(2)) || 0"
      :max="30"
      :min="0"
    />
  </div>
  <div id="multiFunctionTab">
    <MultiFunctionTab />
  </div>
  <div id="batteryStats">
    <BatteryStatistics />
  </div>
  <div id="current-monitor">
    <VisionFeed />
  </div>
  <div id="drone-actions">
    <DroneActions />
  </div>
</template>

<script setup>
// @ is an alias to /src
import PathPlanner from "@/components/pathPlanner/PathPlanner.vue";
import ToggleBtn from "@/components/armButton/ToggleBtn.vue";
import SpeedIndicator from "@/components/speedIndicator/SpeedIndicator.vue";
import BatteryStatistics from "@/components/batteryStats/BatteryStatistics.vue";
// import CurrentMonitor from "@/components/currentMonitor/CurrentMonitor.vue";
import VisionFeed from "@/components/VisionFeed.vue";
// import PwmMonitor from "@/components/pwm/PwmMonitor.vue";
import DroneActions from "@/components/droneActions/DroneActions.vue";
import MultiFunctionTab from "@/components/multiFunctionTab/MultiFunctionTab.vue";
import { store } from "@/store";

// UIKit setup - should automatically propagate to the rest of the Vue app
import UIkit from "uikit";
import Icons from "uikit/dist/js/uikit-icons";
UIkit.use(Icons);
</script>

<style scoped>
body {
  background-color: #eeeeee;
  height: 100%;
}
div {
  height: 100%;
}
#path-planner {
  margin-left: 4%;
  margin-top: 11%;
  height: 95%;
}
#toggleBtn {
  text-align: center;
  width: 22%;
  position: absolute;
  top: 7%;
  z-index: 0;
  margin-left: 2%;
  /* Same width as waypoints list */
}
#speedIndicator {
  width: 29%;
  height: 15%;
  position: absolute;
  right: 0;
  margin: 2%;
  top: 7%;
  border-radius: 15px;
  z-index: 0;
}

#multiFunctionTab {
  position: absolute;
  justify-content: left;
  left: 35.5%;
  width: 29%;
  height: 55%;
  top: 11%;
  z-index: 0;
}

#batteryStats {
  position: absolute;
  width: 29%;
  left: 35.5%;
  bottom: 4%;
  height: 28%;
}

#current-monitor {
  width: 29%;
  height: 30%;
  position: absolute;
  right: 0;
  margin: 2%;
  top: 26%;
  border-radius: 15px;
  z-index: 0;
}

#drone-actions {
  width: 29%;
  height: 30%;
  position: absolute;
  right: 0;
  margin-right: 2%;
  bottom: 4%;
  border-radius: 15px;
  z-index: 0;
}
</style>
