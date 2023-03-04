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
    <div id="current-monitor">
      <CurrentMonitor />
    </div>

    <div id="pwm-monitor">
      <PwmMonitor />
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
import CurrentMonitor from "@/components/currentMonitor/CurrentMonitor.vue";
import PwmMonitor from "@/components/pwm/PwmMonitor.vue";
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
    CurrentMonitor,
    PwmMonitor,
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
  width: 22%;
  position: absolute;
  top: 80px;
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
  top: 70px;
  border-radius: 15px;
  z-index: 0;
}

#notePad {
  position: absolute;
  left: 35.5%;
  width: 29%;
  height: 59%;
  top: 110px;
  z-index: 0;
}

#batteryStats {
  position: absolute;
  width: 29%;
  left: 35.5%;
  bottom: 4%;
  height: 25%;
}

#current-monitor {
  width: 29%;
  height: 30%;
  position: absolute;
  right: 0;
  margin: 2%;
  top: 23%;
  border-radius: 15px;
  z-index: 0;
}

#pwm-monitor {
  width: 29%;
  height: 37%;
  position: absolute;
  right: 0;
  margin-right: 2%;
  bottom: 4%;
  border-radius: 15px;
  z-index: 0;
}
</style>
