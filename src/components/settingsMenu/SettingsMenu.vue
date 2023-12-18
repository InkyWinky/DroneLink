<template>
  <a href="#offcanvas-usage" id="settings-btn" uk-toggle>
    <i class="fa-sharp fa-solid fa-gears icon-btn-effect" id="settings-icon" />
  </a>
  <div id="offcanvas-usage" uk-offcanvas>
    <div class="uk-offcanvas-bar">
      <button class="uk-offcanvas-close" type="button" uk-close></button>

      <h3 class="font-bold text-xl" @click="secret++">Settings</h3>
      <form class="uk-grid-small" uk-grid>
        <div class="uk-width-1-1 uk-padding-remove-left">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_default_alt.valueOf(),
            }"
          >
            Cruise Altitude
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
        <div class="uk-width-1-1 uk-padding-remove-left">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_takeoff_alt.valueOf(),
            }"
          >
            Transition Altitude
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
        <div class="uk-width-1-1 uk-padding-remove-left">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_min_turn_radius.valueOf(),
            }"
          >
            Minimum Turn Radius
          </p>
          <input
            @change="onMinTurnRadiusChange"
            v-model="min_turn_radius"
            class="uk-input"
            type="number"
            placeholder="50"
            aria-label="50"
            color="secondary"
          />
        </div>
        <div class="uk-width-1-1 uk-padding-remove-left">
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

        <div class="uk-width-1-1 uk-padding-remove-left">
          <p
            class="text-start font-bold text-sm"
            :class="{
              'text-blue-500': edited_vtol_mode.valueOf(),
            }"
          >
            VTOL transition to
          </p>
          <select
            class="uk-select"
            v-model="vtol_transition_mode"
            @change="onVTOLModeChange"
          >
            <option value="3">VTOL</option>
            <option value="4">CRUISE</option>
          </select>
        </div>
        <span class="flex flex-row justify-center w-full m-0 p-0">
          <button
            class="uk-button bg-gray-500 hover:bg-gray-600 mx-2 mt-2 border-gray-600 w-1/2"
            @click.prevent="resetForm"
          >
            Reset
          </button>
          <button
            class="uk-button bg-blue-600 hover:bg-blue-700 mx-2 mt-2 border-gray-600 w-1/2"
            type="submit"
            @click.prevent="onSubmit"
          >
            <div
              v-if="isSuccess.valueOf()"
              uk-icon="icon:check; ratio: 1.5"
              class="flex flex-col justify-center items-center text-white relative"
            >
              <div uk-spinner class="flex items-center absolute" />
            </div>
            <p v-else>Submit</p>
          </button>
        </span>
      </form>
      <span class="w-full flex m-4 pr-10">
        <router-link
          to="/payload"
          custom
          v-slot="{ navigate }"
          @click="store.menuClosed.value = !store.menuClosed.value"
        >
          <button
            class="uk-button uk-button-primary justify-center w-full"
            uk-toggle="target: #offcanvas-usage"
            type="button"
            @click="navigate"
          >
            Payload
          </button>
        </router-link>
      </span>
      <div
        v-if="secret > 5"
        class="flex flex-col w-full gap-4 outline outline-white rounded-sm p-2"
      >
        <p class="font-bold text-md">Developer Tools</p>
        <button
          class="rounded-md bg-gray-500 hover:bg-gray-600 w-full"
          @click="patient_location"
        >
          SET PATIENT LOCATION
        </button>
        <button
          class="rounded-md bg-gray-500 hover:bg-gray-600 w-full"
          @click="drop_location"
        >
          SET PAYLOAD DEPLOYMENT LOCATION
        </button>
        <button
          class="rounded-md bg-gray-500 hover:bg-gray-600 w-full"
          @click="ascend_and_rtl"
        >
          RETURN HOME AFTER ASCENDING
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { store } from "@/store";
import api from "@/api";
let default_alt = store?.settings?.default_alt;
let takeoff_alt = store?.settings?.takeoff_alt;
let waypoint_type = store?.settings?.waypoint_type.toString();
let vtol_transition_mode = store?.settings?.vtol_transition_mode.toString();
let min_turn_radius = store?.settings?.min_turn_radius;
let isSuccess = ref(false);
let edited_default_alt = ref(false);
let edited_takeoff_alt = ref(false);
let edited_waypoint_type = ref(false);
let edited_vtol_mode = ref(false);
let edited_min_turn_radius = ref(false);
let secret = ref(0);

// console.log(store?.settings);
// console.log(store.settings.default_alt, default_alt);

const patient_location = () => {
  api.executeCommand("PATIENT_LOCATION", {
    patient_location: {
      lat: -37.54213375308094,
      long: 145.64295397543202,
      alt: store?.settings?.default_alt,
    },
  });
};

const drop_location = () => {
  // dropoff_coordinates, cruise_alt, transition_alt, cardinal_approach
  api.executeCommand("DROP_LOCATION", {
    dropoff_coordinates: {
      lat: -37.543755530521956,
      long: 145.64702276429728,
      alt: 40, // This alt is dependant on user input
    },
    cruise_alt: store?.settings?.default_alt,
    transition_alt: store?.settings?.takeoff_alt,
    cardinal_approach: "SOUTH", // Can be NORTH, EAST, SOUTH or WEST
  });
};

const ascend_and_rtl = () => {
  api.executeCommand("ASCEND_AND_RTL", {
    dropoff_coordinates: {
      lat: -37.5437555305,
      long: 145.64702276429728,
      alt: 40, // This alt is dependant on user input
    },
    cruise_alt: store?.settings?.default_alt,
    transition_alt: store?.settings?.takeoff_alt,
    cardinal_direction: "SOUTH", // Can be NORTH, EAST, SOUTH or WEST
  });
};
const resetForm = () => {
  default_alt = store?.settings?.default_alt;
  takeoff_alt = store?.settings?.takeoff_alt;
  waypoint_type = store?.settings?.waypoint_type.toString();
  min_turn_radius = store?.settings?.min_turn_radius;
  edited_default_alt.value = false;
  edited_takeoff_alt.value = false;
  edited_waypoint_type.value = false;
  edited_min_turn_radius.value = false;
};

const onSubmit = () => {
  console.log("Updating Settings");
  store.settings.default_alt = Number(default_alt);
  store.settings.takeoff_alt = Number(takeoff_alt);
  store.settings.waypoint_type = Number(waypoint_type);
  store.settings.vtol_transition_mode = Number(vtol_transition_mode);
  store.settings.min_turn_radius = Number(min_turn_radius);
  edited_default_alt.value = false;
  edited_takeoff_alt.value = false;
  edited_waypoint_type.value = false;
  edited_vtol_mode.value = false;
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
const onVTOLModeChange = () => {
  edited_vtol_mode.value =
    store?.settings?.vtol_transition_mode != vtol_transition_mode;
};
const onMinTurnRadiusChange = () => {
  edited_min_turn_radius.value = store?.settings?.min_turn_radius;
};
</script>

<style scoped>
#settings-icon {
  color: white;
  font-size: 1.5em;
}
#settings-btn {
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
