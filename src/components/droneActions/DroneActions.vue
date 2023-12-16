<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 15px; padding: 30px; bottom: 4%"
  >
    <h3>DRONE ACTIONS</h3>
    <div id="rtl-container" class="h-auto w-full m-2 p-2 bg-slate-200">
      <button
        id="rtl-btn"
        class="w-full h-auto rounded p-2 flex items-center justify-center"
        @click="RTL()"
      >
        Return to Launch
      </button>
    </div>
    <div id="qloiter-container" class="h-auto w-full m-2 p-2 bg-slate-200">
      <button
        id="qloiter-btn"
        class="w-full h-auto rounded p-2 flex items-center justify-center"
        @click="setQLoiter()"
      >
        Set qLoiter
      </button>
    </div>
  </div>
</template>
<script setup>
import api from "@/api";

function RTL() {
  api.executeCommand("CHANGE_DRONE_MODE", { mode: "RTL" });
}

function setQLoiter() {
  api.executeCommand("CHANGE_DRONE_MODE", { mode: "QLOITER" });
}
</script>

<style scoped></style>
