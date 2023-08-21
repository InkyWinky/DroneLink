<template>
  <a href="#offcanvas-usage" id="settings-btn" uk-toggle>
    <i class="fa-sharp fa-solid fa-gears icon-btn-effect" id="settings-icon" />
  </a>
  <div id="offcanvas-usage" uk-offcanvas>
    <div class="uk-offcanvas-bar">
      <button class="uk-offcanvas-close" type="button" uk-close></button>

      <h3 class="font-bold text-xl">Settings</h3>
      <form class="uk-grid-small" uk-grid @submit.prevent="onSubmit">
        <div class="uk-width-1-1">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_default_alt.valueOf(),
            }"
          >
            Default Waypoint Altitude
          </p>
          <input
            @change="onDefaultAltChange"
            v-model="default_alt"
            class="uk-input"
            type="number"
            placeholder="100"
            aria-label="100"
          />
        </div>
        <div class="uk-width-1-1">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_takeoff_alt.valueOf(),
            }"
          >
            Default Takeoff Altitude
          </p>
          <input
            @change="onTakeoffAltChange"
            v-model="takeoff_alt"
            class="uk-input"
            type="number"
            placeholder="50"
            aria-label="50"
            color="secondary"
          />
        </div>
        <div class="uk-width-1-1">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_waypoint_type.valueOf(),
            }"
          >
            Waypoint Type
          </p>
          <select
            class="uk-select"
            v-model="waypoint_type"
            @change="onWaypointTypeChange"
          >
            <option value="16">WAYPOINT</option>
            <option value="18">LOITER_TURNS</option>
          </select>
        </div>
        <span class="flex flex-row justify-center w-full m-0 p-0">
          <button
            class="uk-button bg-blue-600 hover:bg-blue-700 ml-10 mt-2 border-gray-600"
            type="submit"
          >
            Submit
          </button>

          <div
            uk-icon="icon:check; ratio: 1.5"
            class="ml-2 mt-1 flex items-center text-green-600 relative"
            :class="{ invisible: !isSuccess.valueOf() }"
          >
            <div uk-spinner class="flex items-center absolute" />
          </div>
        </span>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { store } from "@/store";
let default_alt = store?.settings?.default_alt;
let takeoff_alt = store?.settings?.takeoff_alt;
let waypoint_type = store?.settings?.waypoint_type.toString();
let isSuccess = ref(false);
let edited_default_alt = ref(false);
let edited_takeoff_alt = ref(false);
let edited_waypoint_type = ref(false);

console.log(store?.settings);
console.log(store.settings.default_alt, default_alt);
const onSubmit = () => {
  console.log("Updating Settings");
  store.settings.default_alt = Number(default_alt);
  store.settings.takeoff_alt = Number(takeoff_alt);
  store.settings.waypoint_type = Number(waypoint_type);
  edited_default_alt.value = false;
  edited_takeoff_alt.value = false;
  edited_waypoint_type.value = false;
  isSuccess.value = true;
  console.log(isSuccess.value);
  console.log(store.settings);
  setTimeout(() => {
    isSuccess.value = false;
    console.log(isSuccess.value);
  }, 1000);
};

const onDefaultAltChange = () => {
  console.log(
    "DEFAULT ALT CHANGE",
    store?.settings?.default_alt != default_alt
  );
  edited_default_alt.value = store?.settings?.default_alt != default_alt;
};
const onTakeoffAltChange = () => {
  edited_takeoff_alt.value = store?.settings?.takeoff_alt != takeoff_alt;
};
const onWaypointTypeChange = () => {
  edited_waypoint_type.value = store?.settings?.waypoint_type != waypoint_type;
};
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
