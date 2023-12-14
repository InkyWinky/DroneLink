<!-- LiPo Voltage Calculator -->
<script setup>
import { store } from "@/store";
// import { defineProps, computed, ref } from "vue";
import { ref, computed } from "vue";
// Will need to check these voltages but I think it should be OK to set some defaults for now
// const props = defineProps({
//   cellCurrentVoltage: {
//     type: Number,
//     required: false,
//     default: 3.84,
//   },
// });
// let timeRemaining = ref(0); //Calculate time remaining in minutes based on current battery level
// let hoursRemaining = ref(0);
// let minutesRemaining = ref(0);
// hoursRemaining.value = Math.floor(timeRemaining.value / 60);
// minutesRemaining.value = timeRemaining.value % 60;

// Taken from https://blog.ampow.com/lipo-voltage-chart/
// Voltage is for a single cell in series; this is configurable and we can just multiply it by the cell count
// const cellCapacity = {
//   0.0: 3.27,
//   0.05: 3.61,
//   0.1: 3.69,
//   0.15: 3.71,
//   0.2: 3.73,
//   0.25: 3.75,
//   0.3: 3.77,
//   0.35: 3.79,
//   0.4: 3.8,
//   0.45: 3.82,
//   0.5: 3.84,
//   0.55: 3.85,
//   0.6: 3.87,
//   0.65: 3.91,
//   0.7: 3.95,
//   0.75: 3.98,
//   0.8: 4.02,
//   0.85: 4.08,
//   0.9: 4.11,
//   0.95: 4.15,
//   1.0: 4.2,
// };
// This function returns the closest charge percentage based on the input cell count
// Object.entries() returns an array of key-value pairs where the first entry is the key and the second the value
// I think we'll only use this if we want to have a general battery display which includes the current charge percentage rather than just a calculator
// const closestChargeFraction = computed(
//   () =>
//     Object.entries(cellCapacity).reduce((prev, curr) => {
//       return Math.abs(curr[1] * cellCount.value - props.cellCurrentVoltage) <
//         Math.abs(prev[1] * cellCount.value - props.cellCurrentVoltage)
//         ? curr
//         : prev;
//     })[0] * 100
// );
// const nominalVoltage = computed(() => cellCount.value * 3.7);
// const chargedVoltage = computed(() => cellCount.value * 4.2);
// const halfChargeVoltage = computed(() => cellCount.value * cellCapacity[0.5]);
// Below functions handle interactivity and form setup
const maxPropulsion = 33.6;
const minPropulsion = 30.4;

const maxAvionics = 16.8;
const minAvionics = 15.2;
const propulsionPercentage = computed(() => {
  return {
    height: `${
      ((store?.live_data?.propulsion_battery - minPropulsion) /
        (maxPropulsion - minPropulsion) || 0) * 100
    }%`,
  };
});

const avionicsPercentage = computed(() => {
  return {
    height: `${
      ((store?.live_data?.avionics_battery - minAvionics) /
        (maxAvionics - minAvionics) || 0) * 100
    }%`,
  };
});

// const avionicsBatteryColour = computed(() => {
//   if (avionicsPercentage.value.height < 20) {
//     return { color: "red" };
//   } else if (avionicsPercentage.value.height < 40) {
//     return "orange";
//   } else {
//     return "green";
//   }
// });

const avionicsCellCount = ref(4);
const propCellCount = ref(8);
</script>

<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 20px; padding: 8px 20px 20px 20px"
  >
    <h3>BATTERY STATISTICS</h3>
    <div class="cell-calculator-container">
      <div class="statistic">
        <p class="propulsion-total-voltage-stat-display">
          {{ (store?.live_data?.propulsion_battery || "0") + "V" }}
        </p>
        <p class="cell-voltage-stat-display">
          {{
            (store?.live_data?.propulsion_battery / propCellCount || "0") + "V"
          }}
        </p>
        <p class="per-cell-text">per cell</p>
      </div>

      <div class="live-stats-display">
        <div class="propulsion battery-outline">
          <!-- Need a div to center the stuff properly rather than having overlapping text -->
          <!-- <div class="battery-stat-group">
            <span class="battery-stat">{{
              props.cellCurrentVoltage.toFixed(1) + "V"
            }}</span>
            <span class="battery-stat">{{ closestChargeFraction + "%" }}</span>
          </div> -->
          <div id="propulsion-battery-terminal"></div>
          <p class="propulsion battery-label">Propulsion</p>
          <div class="battery-level" :style="propulsionPercentage"></div>
        </div>
        <div class="avionics battery-outline">
          <div id="avionics-battery-terminal"></div>
          <p class="avionics battery-label">Avionics</p>
          <!-- Need a div to center the stuff properly rather than having overlapping text -->
          <div class="battery-level-avionics" :style="avionicsPercentage">
            <!-- <div
              class="wavy-line wavy-line-green"
              data-text="xxxxxxxxxxxxxx"
            ></div> -->
          </div>
        </div>
        <input
          v-model="propCellCount"
          class="propulsion uk-input param-input"
          type="number"
          min="1"
          max="99"
          placeholder="8"
        />
        <!-- <span id="time-remaining"
          >{{ hoursRemaining }}hrs {{ minutesRemaining }}min remaining</span
        > -->
        <input
          v-model="avionicsCellCount"
          class="avionics uk-input param-input"
          type="number"
          min="1"
          max="99"
          placeholder="4"
        />
      </div>

      <div class="computed-statistics">
        <div class="statistic">
          <p class="avionics-total-voltage-stat-display">
            {{ (store?.live_data?.avionics_battery || "0") + "V" }}
          </p>
          <p class="avionics-cell-voltage-stat-display">
            {{
              (store?.live_data?.avionics_battery / avionicsCellCount || "0") +
              "V"
            }}
          </p>
          <p class="avionics-per-cell-text">per cell</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
div {
  height: 100%;
}
h3 {
  font-family: "Aldrich", sans-serif;
  margin-top: 0;
}
/* Object stacks should have equal space between each other, but rely on the padding inherent to the container's parent */
.cell-calculator-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.calculator-cell-count {
  width: 20%;
  text-align: center;
}
.calculator-cell-count > input {
  margin-top: 0.1rem;
  background-color: #ddd;
  text-align: center;
  border-radius: 8px;
}
.live-stats-display {
  flex-grow: 1;
  margin: 4% 4%;
  padding: 0;
  text-align: center;
  position: relative;
}
.battery-outline {
  width: 40%;
  height: 50%;
  border: 5px solid #8ac11f;
  border-radius: 8px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 15%;
}
.propulsion {
  position: absolute;
  left: 0;
}
.avionics {
  position: absolute;
  right: 0;
}

#propulsion-battery-terminal {
  width: 45%;
  height: 6%;
  border-radius: 2px;
  background-color: #8ac11f;
  position: absolute;
  top: -10px;
}

#avionics-battery-terminal {
  width: 45%;
  height: 6%;
  border-radius: 2px;
  background-color: #8ac11f;
  position: absolute;
  top: -10px;
}
.battery-stat-group {
  display: block;
  position: absolute;
  top: 30%;
  transform: translateY(-45%);
}
.battery-stat {
  font-size: 1.5em;
  position: absolute;
  top: 25%;
  transform: translateX(-50%);
}
.computed-statistics {
  width: 20%;
  height: 50%;
  display: flex;
  flex-direction: column;
  transform: translateY(-40%);
  font-size: 0.7em;
}
.statistic {
  margin: 0;
  text-align: center;
}
.stat-header {
  margin: 0;
}
.avionics-total-voltage-stat-display {
  margin: 0;
  padding: 0;
  font-size: 3em;
  color: black;
  padding-top: 2px;
}

.propulsion-total-voltage-stat-display {
  margin: 0;
  padding: 5px 5px 0 5px;
  font-size: 1.5em;
  color: black;
}

.cell-voltage-stat-display {
  margin: 0;
  font-size: 1.2em;
  color: lightslategray;
}

.avionics-cell-voltage-stat-display {
  position: relative;
  margin: 0;
  font-size: 1.6em;
  color: lightslategray;
}

.avionics-total-voltage-stat-display:hover {
  color: #8ac11f;
}
.propulsion-total-voltage-stat-display:hover {
  color: #8ac11f;
}
#time-remaining {
  position: absolute;
  font-size: 0.7em;
  left: 8%;
  bottom: 15%;
}
.param-input {
  width: 40px;
  height: 24px;
  background-color: #ddd;
  border-style: none;
  border-radius: 5px;
  font-size: 0.8em;
  position: absolute;
  bottom: 10%;
}
.battery-label {
  font-size: 0.7em;
  color: black;
  position: absolute;
  bottom: -20px;
}
.battery-level {
  width: 90%;
  height: 15%;
  background-color: #bfd78e;
  position: absolute;
  bottom: 0;
  border-style: none;
  margin: 0;
  padding: 0;
}
.per-cell-text {
  margin: 0;
  font-size: 0.7em;
  color: lightslategray;
  position: relative;
  top: -8px;
}

.avionics-per-cell-text {
  margin: 0;
  font-size: 1em;
  color: lightslategray;
  position: relative;
  top: -8px;
}
.wavy-line {
  width: 100%;
  height: 100px;
  overflow: hidden;
  margin: 0 auto 0 auto;
  text-decoration-color: #bfd78e;
  z-index: 999;
  position: absolute;
  top: -25px;
}
.wavy-line:before {
  content: attr(data-text);
  position: relative;
  top: -35px;
  color: rgba(0, 0, 0, 0);
  width: calc(100% + 27px);
  font-size: 3em;
  text-decoration-style: wavy;
  text-decoration-color: #bfd78e;
  text-decoration-line: underline;
  animation: animate 2.5s ease-in-out infinite;
  -webkit-animation: animate 2.5s ease-in-out infinite;
}

@keyframes animate {
  0% {
    left: -0px;
  }
  100% {
    left: -70px;
  }
}
@-webkit-keyframes animate {
  0% {
    left: -0px;
  }
  100% {
    left: -70px;
  }
}
</style>
