<script setup>
// Prepare to provide
import { provide } from 'vue';
import { reactive } from 'vue';

// UIKit setup - should automatically propagate to the rest of the Vue app
import UIkit from 'uikit';
import Icons from 'uikit/dist/js/uikit-icons';
import SettingsPanel from "./components/SettingsPanel.vue";
import SpeedIndicator from './components/SpeedIndicator.vue';
UIkit.use(Icons);

// Set up global state for settings button - must be reactive
const settingsOpen = reactive({
  value: false
});

// Set up global state for the airspeed
const airspeed = reactive({
  value: 0
});

// Provide the global state to the rest of the app
provide('settingsOpen', settingsOpen);
// Airspeed can be passed in as a prop since we're not modifying it in the speed indicator

// Function for handling the settings modal
function toggleSettings() {
  settingsOpen.value = !settingsOpen.value;
}

</script>

<template>
  <header>
    <!-- This element toggles the settings display -->
    <span uk-icon="icon: settings" class="settings-button" @click="toggleSettings"></span>
  </header>

  <main>
    <!-- Based on the design, we have 6 elements that need to be implemented -->
    <!-- Notes, LiPo Voltage Calculator, Waypoints, Speed, PCB Current, PWM Monitor -->
    <!-- To me, the LiPo voltage calculator and speed seem to be the simplest. PCB current can probably be done as a modified version of the speed indicator, but rotation?? CSS variables? -->

    <!-- Dummy variables for now to make it easy to see where we went wrong. -->
    <SpeedIndicator :airspeed="airspeed.value" :max="150" :min="30" />

    <!-- Let's say that the settings panel goes at the bottom of the element stack for now - it's a modal so it should appear on top of everything anyway. -->
    <SettingsPanel v-if="settingsOpen.value" />

    <input v-model="airspeed.value" type="number" />
  </main>
</template>

<style lang="less">
@import "../node_modules/uikit/src/less/uikit.less";
</style>

