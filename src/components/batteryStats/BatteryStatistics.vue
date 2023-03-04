<!-- LiPo Voltage Calculator -->
<script setup>
import { defineProps, computed, ref } from "vue";
// Will need to check these voltages but I think it should be OK to set some defaults for now
const props = defineProps({
  cellCurrentVoltage: {
    type: Number,
    required: false,
    default: 3.84,
  },
});
// Taken from https://blog.ampow.com/lipo-voltage-chart/
// Voltage is for a single cell in series; this is configurable and we can just multiply it by the cell count
const cellCapacity = {
  0.0: 3.27,
  0.05: 3.61,
  0.1: 3.69,
  0.15: 3.71,
  0.2: 3.73,
  0.25: 3.75,
  0.3: 3.77,
  0.35: 3.79,
  0.4: 3.8,
  0.45: 3.82,
  0.5: 3.84,
  0.55: 3.85,
  0.6: 3.87,
  0.65: 3.91,
  0.7: 3.95,
  0.75: 3.98,
  0.8: 4.02,
  0.85: 4.08,
  0.9: 4.11,
  0.95: 4.15,
  1.0: 4.2,
};
// This function returns the closest charge percentage based on the input cell count
// Object.entries() returns an array of key-value pairs where the first entry is the key and the second the value
// I think we'll only use this if we want to have a general battery display which includes the current charge percentage rather than just a calculator
const closestChargeFraction = computed(
  () =>
    Object.entries(cellCapacity).reduce((prev, curr) => {
      return Math.abs(curr[1] * cellCount.value - props.cellCurrentVoltage) <
        Math.abs(prev[1] * cellCount.value - props.cellCurrentVoltage)
        ? curr
        : prev;
    })[0] * 100
);
const nominalVoltage = computed(() => cellCount.value * 3.7);
const chargedVoltage = computed(() => cellCount.value * 4.2);
const halfChargeVoltage = computed(() => cellCount.value * cellCapacity[0.5]);
// Below functions handle interactivity and form setup
const cellCount = ref(0);
</script>

<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 20px; padding: 20px"
  >
    <h3>BATTERY STATISTICS</h3>
    <div class="cell-calculator-container">
      <div class="calculator-cell-count statistic">
        <span class="stat-header">Cell Count</span>
        <input
          v-model="cellCount"
          class="uk-input"
          type="text"
          placeholder="0"
        />
      </div>

      <div class="live-stats-display">
        <div class="battery-outline">
          <div class="battery-terminal negative-terminal">
            <span class="terminal-text">-</span>
          </div>
          <div class="battery-terminal positive-terminal">
            <span class="terminal-text">+</span>
          </div>
          <!-- Need a div to center the stuff properly rather than having overlapping text -->
          <div class="battery-stat-group">
            <span class="battery-stat">{{
              props.cellCurrentVoltage.toFixed(1) + "V"
            }}</span>
            <span class="battery-stat">{{ closestChargeFraction + "%" }}</span>
          </div>
        </div>
      </div>

      <div class="computed-statistics">
        <div class="statistic">
          <span class="stat-header">Nominal voltage</span>
          <p class="stat-display">{{ nominalVoltage.toFixed(1) + "V" }}</p>
        </div>

        <div class="statistic">
          <span class="stat-header">Charged</span>
          <p class="stat-display">{{ chargedVoltage.toFixed(1) + "V" }}</p>
        </div>

        <div class="statistic">
          <span class="stat-header">50%</span>
          <p class="stat-display">{{ halfChargeVoltage.toFixed(1) + "V" }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  margin-top: 0.2rem;
  background-color: #ddd;
  text-align: center;
  border-radius: 8px;
}
.live-stats-display {
  height: 100%;
  flex-grow: 1;
  margin: 0 8%;
  padding: 0 5%;
  text-align: center;
  position: relative;
}
.battery-outline {
  width: 100%;
  height: 0;
  margin-top: 20%;
  padding-bottom: 65.6%;
  border: 2px solid black;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.battery-terminal {
  position: absolute;
  width: 15%;
  height: 20%;
  top: 0;
  border: 2px solid black;
  display: flex;
  justify-content: center;
  align-items: center;
  transform: translateY(-100%);
}
.negative-terminal {
  left: 10%;
}

.positive-terminal {
  right: 10%;
}
.battery-stat-group {
  display: block;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}
.battery-stat {
  display: block;
}
.computed-statistics {
  width: 20%;
  height: 50%;
  display: flex;
  flex-direction: column;
  transform: translateY(-70%);
}
.statistic {
  margin: 0;
  text-align: center;
}
.stat-header {
  margin: 0;
}
.stat-display {
  margin: 0;
  padding: 0;
  background-color: #ccc;
  border-radius: 5px;
  width: 100%;
}
</style>
