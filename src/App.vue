<template>
  <nav>
    <div class="flex w-full items-center">
      <div class="w-1/3"></div>
      <div
        id="vision-detection-eye-true"
        v-if="vision_detection_bool"
        @click="toggleVisionDetection(vision_detection_bool)"
      >
        <svg
          id="vision-detection-on-svg"
          fill="#ffffff"
          height="30px"
          width="30px"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          viewBox="0 0 488.85 488.85"
          xml:space="preserve"
          stroke="#ffffff"
        >
          <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            stroke-linecap="round"
            stroke-linejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            <g>
              <path
                d="M244.425,98.725c-93.4,0-178.1,51.1-240.6,134.1c-5.1,6.8-5.1,16.3,0,23.1c62.5,83.1,147.2,134.2,240.6,134.2 s178.1-51.1,240.6-134.1c5.1-6.8,5.1-16.3,0-23.1C422.525,149.825,337.825,98.725,244.425,98.725z M251.125,347.025 c-62,3.9-113.2-47.2-109.3-109.3c3.2-51.2,44.7-92.7,95.9-95.9c62-3.9,113.2,47.2,109.3,109.3 C343.725,302.225,302.225,343.725,251.125,347.025z M248.025,299.625c-33.4,2.1-61-25.4-58.8-58.8c1.7-27.6,24.1-49.9,51.7-51.7 c33.4-2.1,61,25.4,58.8,58.8C297.925,275.625,275.525,297.925,248.025,299.625z"
              ></path>
            </g>
          </g>
        </svg>
      </div>
      <div
        id="vision-detection-eye-false"
        v-else
        @click="toggleVisionDetection(vision_detection_bool)"
      >
        <svg
          id="vision-detection-off-svg"
          fill="#ffffff"
          stroke="#ffffff"
          height="30px"
          width="30px"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          viewBox="0 0 24 24"
        >
          <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            stroke-linecap="round"
            stroke-linejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            <path
              stroke="#ffffff"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 10a13.358 13.358 0 0 0 3 2.685M21 10a13.358 13.358 0 0 1-3 2.685m-8 1.624L9.5 16.5m.5-2.19a10.59 10.59 0 0 0 4 0m-4 0a11.275 11.275 0 0 1-4-1.625m8 1.624.5 2.191m-.5-2.19a11.275 11.275 0 0 0 4-1.625m0 0 1.5 1.815M6 12.685 4.5 14.5"
            ></path>
          </g>
        </svg>
      </div>
      <router-link
        to="/"
        class="flex flex-row w-1/3 items-center justify-center"
      >
        <img src="../public/logo.png" class="h-10" />
        <p class="text-white">DroneLink</p>
      </router-link>
      <div class="w-1/3 flex justify-end">
        <ConnectionStatus />
      </div>
    </div>

    <!-- <div id="drone-connection">
      <span
        uk-icon="refresh"
        class="pr-2 cursor-pointer"
        @click="onSyncDrone()"
      ></span>
      <span>Drone Connection</span>
      <div
        :id="
          store.live_data?.drone_connected
            ? 'connection-status-on'
            : 'connection-status-off'
        "
      ></div>
    </div> -->
  </nav>
  <SettingsMenu />
  <router-view></router-view>
</template>

<script>
import { ref } from "vue";
import { store } from "./store";
import { api } from "./api";
import SettingsMenu from "./components/settingsMenu/SettingsMenu.vue";
import ConnectionStatus from "./components/ConnectionStatus.vue";
// import toggleSettingsMenu from "./store";

export default {
  setup() {
    const vision_detection_bool = ref(false);

    return { store, api, vision_detection_bool };
  },
  components: { SettingsMenu, ConnectionStatus },
  methods: {
    toggleVisionDetection(vision_detection_bool) {
      if (
        vision_detection_bool &&
        confirm("Confirm disable Vision detection?")
      ) {
        console.log("[MESSAGE] Disabling Vision detection");
        api.executeCommand("TOGGLE_VISION_DETECTION", {});
      } else if (confirm("Confirm enable Vision detection?")) {
        console.log("[MESSAGE] Enabling Vision detection");
        api.executeCommand("TOGGLE_VISION_DETECTION", {});
      }
      vision_detection_bool = !vision_detection_bool;
    },
  },
};
</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;
#app {
  font-family: "Aldrich", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100%;
}
.connect-btn {
  font-size: 1em !important;
}
#logo-link {
  height: 2%;
  width: 2%;
  position: absolute;
  left: 51.5%;
}
html {
  height: 100%;
}
body {
  height: 100%;
  overflow-y: hidden;
  margin: 0;
  background-color: #eeeeee;
}
nav {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
  padding: 5px;
  margin: 0;
  text-decoration: none;
}

nav a {
  font-weight: normal;
  font-size: 2.5em;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: white;
  font-size: 2em;
  -webkit-font-smoothing: antialiased;
}
#settings-icon {
  color: white;
  font-size: 1.5em;
}

#drone-connection {
  color: white;
  position: absolute;
  right: 20px;
  top: 1.8%;
  font-family: "Open Sans", sans-serif;
  font-size: 1.5em;
  -webkit-font-smoothing: antialiased;
}
#connection-status-on {
  background-color: greenyellow;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  margin: 20px;
  margin-top: 16px;
  box-shadow: 0 0 5px 2px greenyellow;
}
#connection-status-off {
  background-color: red;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  margin: 20px;
  margin-top: 16px;
  box-shadow: 0 0 5px 2px red;
}

#vision-detection-eye-true {
  position: absolute;
  left: 80px;
}

#vision-detection-eye-false {
  position: absolute;
  left: 80px;
}
/* 
#vision-detection-on-svg:hover {
  fill: #9198e5;
}

#vision-detection-off-svg:hover {
  fill: #9198e5;
} */
</style>
