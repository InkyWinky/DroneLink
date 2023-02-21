<template>
  <div id="toggleWrapper">
    <input type="checkbox" id="switch" v-model="isChecked" /><label
      id="toggleLabel"
      for="switch"
    ></label>
    <span v-if="!isChecked" id="disarmedText">Disarmed</span>
    <span v-if="isChecked" id="armedText">Armed</span>
    <img
      v-if="isChecked"
      id="propellerImg"
      src="../../../public/propeller.png"
      alt=""
    />
  </div>
</template>
<script setup>
import { ref } from "vue";
let isChecked = ref(false);
</script>
<style>
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
  top: 33px;
  right: 6px;
  z-index: 1;
  pointer-events: none;
  animation: rotation 1s ease-out;
}
@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

#toggleLabel {
  cursor: pointer;
  text-indent: -9999px;
  width: 100%;
  height: 100px;
  background: grey;
  display: block;
  border-radius: 100px;
  position: relative;
}
#disarmedText {
  position: relative;
  display: inline-block;
  font-size: 2em;
  transform: translate(0px, -70px);
}
#armedText {
  position: relative;
  display: inline-block;
  font-size: 2em;
  transform: translate(-15px, -70px);
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
