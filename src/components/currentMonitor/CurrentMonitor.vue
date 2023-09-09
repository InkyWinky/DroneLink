<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    id="current-display"
    style="border-radius: 15px; padding: 30px"
  >
    <h3>PCB CURRENT (A)</h3>
    <!-- Current needle -->
    <div class="current-needle" @click="increaseCurrent" @mouseup="stopCurrent">
      <div
        id="needle"
        :style="{
          transform: 'translate(-50%, 22%) ' + 'rotate(' + degrees + 'deg)',
        }"
      ></div>
      <div id="circle">
        <div id="current-value">
          {{ current }}
        </div>
      </div>
    </div>

    <!-- Min and max current -->
    <span id="min-current">{{ minCurrent }}</span>
    <span id="max-current">{{ maxCurrent }}</span>
  </div>
</template>
<script setup>
import { ref } from "vue";
let current = ref(0);
let minCurrent = ref(0);
let maxCurrent = ref(10);
let degrees = ref(0);
degrees.value =
  (current.value - (maxCurrent.value - minCurrent.value) / 2) *
  (120 / ((maxCurrent.value - minCurrent.value) / 2));

function increaseCurrent() {
  if (current.value < maxCurrent.value) {
    current.value++;
  } else {
    current.value = 0;
  }
  degrees.value =
    (current.value - (maxCurrent.value - minCurrent.value) / 2) *
    (120 / ((maxCurrent.value - minCurrent.value) / 2));
}
</script>
<style scoped>
div {
  height: 100%;
}
#current-display {
  background-image: url("../../../public/currentMonitor.png");
  background-repeat: no-repeat;
  background-size: 50% 60%;
  background-position: 50% 54%;
  /* set bg image to the current-display so that we can centre the current needle */
}
#min-current {
  position: absolute;
  bottom: 13%;
  left: 25%;
}

#max-current {
  position: absolute;
  bottom: 13%;
  right: 25%;
}

#needle {
  width: 8px;
  height: 45%;
  background-color: black;
  border-radius: 5px;
  transform-origin: 50% 66%;
}

#circle {
  color: black;
  width: 65px;
  height: 65px;
  background-color: white;
  border: 8px solid black;
  border-radius: 50%;
  transform: translate(-50%, -73%);
  font-size: 2em;
  font-weight: bold;
  display: flex;
  align-items: center;
  position: relative;
}

#current-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -35%);
}

.current-needle {
  position: absolute;
  left: 50%;
}
</style>
