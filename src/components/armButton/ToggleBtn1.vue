<template>
  <div>
    <!-- Check box for activating toggle animations and storing toggle data -->
    <label class="toggle">
      <input type="checkbox" />
      <span class="movingCircle"></span>
    </label>
    Disarmed
  </div>
</template>
<script setup></script>
<style>
.toggle input {
  display: none;
}

.toggle {
  display: inline-block;
  width: 20%; /*=w*/
  height: 5%; /*=h*/
  margin: 4px;
  transform: translate(80%, 50%);
  position: relative;
}

.movingCircle {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  border-radius: 30px;
  box-shadow: 0 0 0 2px #777, 0 0 4px #777;
  cursor: pointer;
  border: 4px solid transparent;
  overflow: hidden;
  transition: 0.2s;
}

.movingCircle:before {
  position: absolute;
  content: "";
  width: 100%;
  height: 100%;
  background-color: #777;
  border-radius: 30px;
  transform: translateX(-30px); /*translateX(-(w-h))*/
  transition: 0.2s;
}

input:checked + .movingCircle:before {
  transform: translateX(30px); /*translateX(w-h)*/
  background-color: limeGreen;
}

input:checked + .movingCircle {
  box-shadow: 0 0 0 2px limeGreen, 0 0 8px limeGreen;
}
</style>
