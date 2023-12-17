<template>
  <AlertNotif
    alertMessage="Vision detection turned on"
    v-if="showDetectionOnAlert"
  />
  <AlertNotif
    alertMessage="Vision detection turned off"
    v-if="showDetectionOffAlert"
  />
  <AlertNotif
    alertMessage="Weathervaning turned on"
    v-if="showWeatherVaningOnAlert"
  />
  <AlertNotif
    alertMessage="Weathervaning turned off"
    v-if="showWeatherVaningOffAlert"
  />
  <nav>
    <div class="flex w-full items-center">
      <div class="w-1/3 flex items-center gap-10">
        <div class="ml-2 z-[99999]">
          <SettingsMenu />
        </div>
        <!-- Vision Toggle Button START -->
        <div
          id="vision-detection-eye-true"
          class="cursor-pointer"
          v-if="vision_on"
          @click="store.vision_on = !store.vision_on"
        >
          <svg
            :class="{
              ' fill-[#ADFF2F]': store.vision_on,
              'fill-white': !store.vision_on,
            }"
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
          class="cursor-pointer"
          v-else
          @click="store.vision_on = !store.vision_on"
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
        <!-- Vision Toggle Button END -->
        <!-- Weathervaning Toggle Button START -->
        <div v-if="isWeatherVaneLoading.valueOf()">
          <div
            uk-spinner
            class="flex items-center h-20 w-20 -my-4 text-white"
          />
        </div>
        <div
          v-else
          class="cursor-pointer h-12 w-16 -mx-4 -mt-3"
          @click="toggleWeatherVaning"
        >
          <svg
            :class="{
              ' fill-[#ADFF2F]': store?.live_data?.weather_vaning,
              'fill-white': !store?.live_data?.weather_vaning,
            }"
            version="1.0"
            xmlns="http://www.w3.org/2000/svg"
            width="225.000000pt"
            height="225.000000pt"
            viewBox="0 0 225.000000 225.000000"
            preserveAspectRatio="xMidYMid meet"
          >
            <g
              transform="translate(0.000000,225.000000) scale(0.100000,-0.100000)"
            >
              <path
                d="M825 1696 c-77 -24 -146 -45 -153 -47 -8 -2 46 -22 120 -43 191 -56
              176 -53 156 -29 -10 11 -18 23 -18 26 0 4 38 7 85 7 l85 0 0 -170 c0 -144 -2
              -172 -15 -177 -24 -8 -45 -57 -45 -102 l0 -40 -60 21 c-33 11 -60 25 -60 32 0
              20 -34 46 -59 46 -34 0 -58 -17 -65 -45 -13 -53 37 -93 91 -74 23 9 40 6 93
              -14 l65 -25 -30 -12 c-16 -6 -73 -27 -125 -46 l-95 -35 -36 21 c-85 47 -169 2
              -169 -91 0 -43 56 -99 100 -99 58 0 109 42 110 90 0 24 9 29 108 64 59 22 113
              41 120 44 9 3 12 -49 12 -242 l0 -246 85 0 85 0 0 246 c0 193 3 245 13 242 6
              -3 60 -22 120 -44 98 -35 107 -40 107 -64 1 -48 52 -90 110 -90 44 0 100 56
              100 99 0 93 -84 138 -169 91 l-36 -21 -95 35 c-52 19 -108 40 -125 46 l-30 12
              65 25 c53 20 70 23 93 14 54 -19 104 21 91 74 -7 29 -31 45 -67 45 -24 0 -57
              -27 -57 -47 0 -6 -27 -20 -60 -31 l-60 -21 0 40 c0 45 -21 94 -45 102 -13 5
              -15 33 -15 177 l0 170 83 0 c79 0 85 -1 112 -30 28 -30 30 -30 137 -30 59 0
              108 4 108 8 0 4 -16 23 -35 42 -19 19 -35 39 -35 45 0 6 16 26 35 45 19 19 35
              38 35 42 0 4 -49 8 -108 8 -107 0 -109 0 -137 -30 -27 -29 -33 -30 -111 -30
              l-83 0 -3 28 c-2 19 -9 27 -23 27 -14 0 -21 -8 -23 -27 l-3 -28 -92 0 -91 0
              29 30 c16 17 27 29 24 29 -2 -1 -67 -20 -144 -43z"
              />
            </g>
          </svg>
        </div>
        <!-- Weathervaning Toggle Button END -->
      </div>

      <router-link
        to="/"
        class="flex flex-row w-1/3 items-center justify-center"
      >
        <img src="../../public/logo.png" class="h-10" />
        <p class="text-white text-3xl">DroneLink</p>
      </router-link>
      <div class="w-1/3 flex justify-end">
        <ConnectionStatus />
      </div>
    </div>
  </nav>
</template>

<script setup>
import ConnectionStatus from "./ConnectionStatus.vue";
import AlertNotif from "./AlertNotif.vue"; // import toggleSettingsMenu from "./store";
import SettingsMenu from "./settingsMenu/SettingsMenu.vue";
import { ref, watch, computed } from "vue";
import { store } from "@/store";
import api from "@/api";

const showDetectionOnAlert = ref(false);
const showDetectionOffAlert = ref(false);
const vision_on = computed(() => store.vision_on);
const isWeatherVaneLoading = ref(false);
const showWeatherVaningOnAlert = ref(false);
const showWeatherVaningOffAlert = ref(false);
const weather_vaning = computed(() => store?.live_data?.weather_vaning);
watch(vision_on, (newVal) => {
  if (newVal == true) {
    showDetectionOnAlert.value = true;
    setTimeout(() => {
      showDetectionOnAlert.value = false;
    }, 3000);
  } else {
    showDetectionOffAlert.value = true;
    setTimeout(() => {
      showDetectionOffAlert.value = false;
    }, 3000);
  }
});

watch(weather_vaning, (newVal) => {
  if (newVal == true) {
    showWeatherVaningOnAlert.value = true;
    setTimeout(() => {
      showWeatherVaningOnAlert.value = false;
    }, 3000);
  } else {
    showWeatherVaningOffAlert.value = true;
    setTimeout(() => {
      showWeatherVaningOffAlert.value = false;
    }, 3000);
    isWeatherVaneLoading.value = false;
  }
});

const toggleWeatherVaning = () => {
  console.log("Toggling weathervaning");
  isWeatherVaneLoading.value = true;
  api.executeCommand("TOGGLE_WEATHER_VANING", {});
  setTimeout(() => {
    isWeatherVaneLoading.value = false;
  }, 2000);
};
</script>

<style scoped>
.connect-btn {
  font-size: 1em !important;
}
#logo-link {
  height: 2%;
  width: 2%;
  position: absolute;
  left: 51.5%;
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

#drone-connection {
  color: white;
  position: absolute;
  right: 20px;
  top: 1.8%;
  font-family: "Open Sans", sans-serif;
  font-size: 1.5em;
  -webkit-font-smoothing: antialiased;
}
/* 
#vision-detection-on-svg:hover {
  fill: #9198e5;
}

#vision-detection-off-svg:hover {
  fill: #9198e5;
} */
</style>
