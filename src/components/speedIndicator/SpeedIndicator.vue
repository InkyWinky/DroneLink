<script setup>
import { defineProps } from "vue";
import { computed } from "vue";
// There are three props that should be defined:
// 1. The airspeed
// 2. Lower bound for airspeed
// 3. Upper bound for airspeed
const props = defineProps({
  airspeed: {
    type: Number,
    required: true,
  },
  max: {
    type: Number,
    required: true,
  },
  // Minimum speed can default to 0
  min: {
    type: Number,
    required: false,
    default: 0,
  },
});
// We need to calculate the percentage of the airspeed relative to the min and max
// This is used to position the needle
const airspeedPercent = computed(() => {
  return {
    left: `${((props.airspeed - props.min) / (props.max - props.min)) * 100}%`,
  };
});
</script>

<template>
  <!-- An airspeed indicator using a bar with a floating needle on top which moves horizontally to the right as the airspeed increases. -->
  <!-- This is rendered as a UIKit card -->
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 15px; padding: 20px"
  >
    <h3>AIRSPEED</h3>
    <!-- We need a custom div here in order to show the speed gradient -->
    <div class="speed-bar">
      <!-- Display min and max at either end of the bar -->
      <span class="uk-text-meta text-outside-top-left">{{ min }}</span>
      <span class="uk-text-meta text-outside-top-right">{{ max }}</span>

      <!-- Display the needle -->
      <div class="speed-display">
        <div class="speed-needle" :style="airspeedPercent">
          <span class="needle"></span>
          <span class="speed-text uk-text-meta">{{ airspeed }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* The speed bar uses a three-step gradient */
.speed-bar {
  width: 100%;
  height: 2rem;
  background-image: linear-gradient(to right, red, yellow, green, yellow, red);
  margin-bottom: 2rem !important; /* Need to override uk-card-body bottom margin to leave space for the speed needle */
}
.text-outside-top-left {
  float: left;
  transform: translateY(-100%) translateX(-50%);
}
.text-outside-top-right {
  float: right;
  transform: translateY(-100%) translateX(50%);
}
.speed-display {
  width: 100%;
  position: relative;
  top: 10%;
  display: flex;
  flex-direction: row;
}
.speed-needle {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateX(-50%);
}
/* The needle is a div with a border */
.needle {
  position: relative;
  display: inline-block;
  vertical-align: middle;
  color: #666;
  box-sizing: border-box;
  width: 0;
  height: 0;
  border: 7px solid transparent;
  border-top: 7px solid;
  border-right: 7px solid;
  margin-top: 0.25rem;
  transform: translateY(52%) rotate(-45deg);
}
.speed-text {
  padding: 0.1rem 1rem;
  background-color: #666;
  color: white;
}
</style>
