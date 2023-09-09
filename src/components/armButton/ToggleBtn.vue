<template>
  <div id="toggleWrapper">
    <input type="checkbox" :checked="store.live_data?.armed" /><label
      id="toggleLabel"
      @click="toggleArm()"
      aria-disabled
      for=""
    ></label>
    <span
      v-if="isLoading.valueOf()"
      id="disarmedText"
      class="pointer-events-none"
      >LOADING...</span
    >
    <span
      v-else-if="!store.live_data?.armed"
      id="disarmedText"
      class="pointer-events-none"
      >DISARMED</span
    >
    <span v-else id="armedText" class="pointer-events-none">ARMED</span>
    <img
      v-if="store.live_data?.armed"
      id="propellerImg"
      src="../../../public/propeller.png"
      alt=""
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../../api.js";
import { store } from "./../../store";

const isLoading = ref(false);
const armConfirmed = ref(false);
async function toggleArm() {
  if (isLoading.value) {
    return;
  }
  isLoading.value = true;
  console.log(isLoading.value);
  console.log("Confirming arm");
  if (confirm("Confirm Arm?")) {
    armConfirmed.value = true;
  } else {
    isLoading.value = false;
    return;
  }

  console.log("toggleArm button pressed");
  api.executeCommand("TOGGLE_ARM", {});
  setTimeout(function () {
    isLoading.value = false;
  }, 3000);
}
</script>

<style scoped>
input[type="checkbox"] {
  height: 0;
  width: 0;
  visibility: hidden;
}
#toggleWrapper {
  margin-left: 15%;
  width: 100%;
  height: 100px;
  position: relative;
}
#propellerImg {
  height: 80px;
  position: absolute;
  top: 38px;
  right: 5px;
  z-index: 1;
  pointer-events: none;
  animation: rotation 1s ease-out;
}
@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

#toggleLabel {
  cursor: pointer;
  text-indent: -9999px;
  width: 100%;
  height: 100px;
  background: #c3534d;
  display: block;
  border-radius: 100px;
  position: relative;
}
#disarmedText {
  position: relative;
  display: inline-block;
  font-size: 1.6em;
  padding-left: 22%;
  transform: translate(10px, -67px);
  color: rgb(61, 0, 0);
}
#armedText {
  position: relative;
  display: inline-block;
  font-size: 1.6em;
  padding-right: 20%;
  transform: translate(-3px, -67px);
}
#toggleLabel:after {
  content: "";
  position: absolute;
  top: 5px;
  left: 5px;
  width: 90px;
  height: 90px;
  background: #fff;
  border-radius: 90px;
  transition: 0.3s;
}

input:checked + #toggleLabel {
  background: #bada55;
}

input:checked + #disarmedText {
  display: none;
}

input:checked + #toggleLabel:after {
  left: calc(100% - 5px);
  transform: translateX(-100%);
}

#toggleLabel:active:after {
  width: 130px;
}
</style>
