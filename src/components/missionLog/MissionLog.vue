<template>
  <div id="mission-log">
    <h3>MISSION LOG</h3>
    <button v-if="store == 'Target found'" @click="loadPayload()">
      Button
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import store from "src/store";

// someone implement backend link to know what the status is
const showPayload = ref(false);

function loadPayload() {
  if (confirm("Open Payload UI?")) {
    showPayload.value = true;
  }
}
</script>

<style></style>
