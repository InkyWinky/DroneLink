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
  <div id="video-feed"></div>
  <div id="overlay">
    <div id="payload-info">
      <!-- info about payload -->
      <p id="payload-height">{{ store?.live_data?.payload?.height }}</p>
      <p id="payload-vel">{{ store?.live_data?.payload?.velocity }}</p>
    </div>
    <div id="aircraft-info">
      <!-- info about aircraft -->
      <p id="alb-height">{{ store?.live_data?.albatross?.ground_height }}</p>
      <p id="alb-vel">{{ store?.live_data?.albatross?.velocity }}</p>
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
    <button @click="deploy()">Deploy Payload</button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { store } from "@/store";

const status = ref("");

function deploy() {
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
