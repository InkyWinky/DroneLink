<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    id="current-display"
    style="border-radius: 15px; padding: 30px"
  >
    <h3>PCB MONITOR (A)</h3>
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
<style>
#current-display {
  background-image: url("../../../public/currentMonitor.png");
  background-repeat: no-repeat;
  background-size: 60% 60%;
  background-position: center center;
  /* set bg image to the current-display so that we can centre the current needle */
}
#min-current {
  position: absolute;
  bottom: 18%;
  left: 20%;
}

#max-current {
  position: absolute;
  bottom: 18%;
  right: 20%;
}

#needle {
  width: 10px;
  height: 45%;
  background-color: black;
  border-radius: 5px;
  transform-origin: 50% 66%;
}

#circle {
  color: black;
  width: 73px;
  height: 73px;
  background-color: white;
  border: 10px solid black;
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
  transform: translate(-50%, -30%);
}

.current-needle {
  position: absolute;
  left: 50%;
}
</style>
