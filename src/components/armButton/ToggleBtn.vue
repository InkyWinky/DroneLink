<template>
  <div id="toggleWrapper">
    <input type="checkbox" id="switch" v-model="isChecked" /><label
      id="toggleLabel"
      for="switch"
    ></label>
    <span v-if="!isChecked" id="disarmedText">DISARMED</span>
    <span v-if="isChecked" id="armedText">ARMED</span>
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
  font-size: 2em;
  transform: translate(10px, -78px);
  color: rgb(61, 0, 0);
}
#armedText {
  position: relative;
  display: inline-block;
  font-size: 2em;
  transform: translate(-3px, -78px);
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
