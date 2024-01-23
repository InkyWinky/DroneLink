<template>
  <div id="gimbal-container">
    <button class="h-auto ctrl-btn shiny-pink-btn" @click="changeToNeutralMode">
      Neutral Mode
    </button>
    <button
      class="h-auto ctrl-btn shiny-pink-btn"
      @click="changeToTargetTrackingMode"
    >
      Target Tracking Mode
    </button>
    <button
      class="h-auto ctrl-btn shiny-pink-btn"
      @click="changeToGpsTrackingMode"
    >
      GPS Tracking Mode
    </button>
    <button class="h-auto ctrl-btn shiny-pink-btn" @click="changeToResetMode">
      Reset Position
    </button>
  </div>
</template>
<script setup>
import api from "@/api";
function changeToNeutralMode() {
  api.executeCommand("GIMBAL_NEUTRAL");
}
function changeToTargetTrackingMode() {
  api.executeCommand("GIMBAL_TRACK_TARGET");
}
function changeToGpsTrackingMode() {
  api.executeCommand("GIMBAL_GPS_TARGET");
}
function changeToResetMode() {
  api.executeCommand("GIMBAL_RESET_POSITION");
}
</script>
<style scoped>
.ctrl-btn {
  font-size: 1.2em;
  color: white;
  padding: 10px;
  margin: 10px;
  width: 80%;
  border-radius: 5px;
}
#gimbal-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  justify-content: center;
}
</style>
