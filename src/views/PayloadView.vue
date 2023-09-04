<!-- 
  [ ] failsafes:
      [ ] failsafe 1
      [ ] failsafe 2
  [ ] payload info:
      [ ] ground height
      [ ] velocity
  [ ] aircraft info:
      [ ] aircraft height from takeoff
      [ ] aircraft ground height
  [ ] status bar
  [ ] go button
 -->
<template>
  <div id="payload-info">
    <!-- info about payload -->
  </div>
  <div id="aircraft-info">
    <!-- info about aircraft -->
  </div>
  <div id="status-bar">
    <span id="payload-status">Status: {{ status }}</span>
  </div>
  <div id="failsafe-one">
    <button @click="failsafeOne()">Failsafe 1</button>
  </div>
  <div id="failsafe-two">
    <button @click="failsafeTwo()">Failsafe 2</button>
  </div>
  <button @click="go()">Go</button>
</template>

<script setup>
import { ref } from "vue";

const status = ref("");

status.value = 3;

function go() {
  if (confirm("Confirm deploy payload?")) {
    // send message to payload system to execute payload delivery
  }
}

function failsafeOne() {
  if (confirm("Confirm failsafe 1?")) {
    // send message to payload system
  }
}

function failsafeTwo() {
  if (confirm("Confirm failsafe 2?")) {
    // send message to payload system
  }
}
</script>
<style>
#status-bar {
  color: blue;
}
</style>
