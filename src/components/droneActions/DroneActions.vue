<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 15px; padding: 10px 30px; bottom: 4%"
  >
    <h3>DRONE ACTIONS</h3>
    <div class="h-auto w-full m-2 p-1 bg-slate-200 action-btn">
      <button
        class="w-full h-auto rounded p-2 flex items-center justify-center"
        @click="setLoiter()"
      >
        LOITER
      </button>
    </div>
    <div class="h-auto w-full m-2 p-1 bg-slate-200 action-btn">
      <button
        class="w-full h-auto rounded p-2 flex items-center justify-center"
        @click="RTL()"
      >
        RTL
      </button>
    </div>
    <div class="action-btn h-auto w-full m-2 p-1 bg-slate-200">
      <button
        id="qloiter-btn"
        class="w-full h-auto rounded p-2 flex items-center justify-center"
        @click="setQLoiter()"
      >
        QLOITER
      </button>
    </div>
  </div>
</template>
<script setup>
import api from "@/api";

function setLoiter() {
  api.executeCommand("CHANGE_DRONE_MODE", { mode: "LOITER" });
}
function RTL() {
  api.executeCommand("CHANGE_DRONE_MODE", { mode: "RTL" });
}

function setQLoiter() {
  api.executeCommand("CHANGE_DRONE_MODE", { mode: "QLOITER" });
}
</script>

<style scoped>
.action-btn {
  border-radius: 5px;
  color: black;
}
.action-btn:hover {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
  color: white;
}
</style>
