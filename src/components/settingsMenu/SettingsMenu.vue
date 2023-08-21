<template>
  <button class="transparentBtn" id="settings-btn" @click="toggleSettingsMenu">
    <i class="fa-sharp fa-solid fa-gears icon-btn-effect" id="settings-icon">
    </i>
  </button>

  <div class="settings-menu" :style="{ width: menuWidth }">
    <!-- Default alt, default takeoff height..etc. -->
  </div>
</template>
<script setup>
import { menuWidth, toggleSettingsMenu } from "@/store";
</script>
<style scoped>
#settings-btn {
  position: absolute;
  left: 20px;
  top: 2%;
  z-index: 2;
}
#settings-btn:hover {
  transform: scale(1.1, 1.1);
  transition: 0.1s ease-in;
}
.settings-menu {
  color: white;
  background-color: #6b7084;
  float: left;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  bottom: 0;
  padding: 0;
  width: 0;

  transition: 0.3s ease;
  display: flex;
  flex-direction: column;
}
</style>
