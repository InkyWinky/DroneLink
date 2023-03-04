<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    id="pwm-bg"
    style="border-radius: 15px; padding: 30px"
  >
    <h3>PWM MONITOR</h3>
  </div>

  <div class="wrapper" id="motor1-wrapper">
    <label for="motor1">motor 1</label>
    <span class="pwm-value" id="motor1">{{ motor1Pwm }}</span>
  </div>

  <div class="wrapper" id="motor2-wrapper">
    <label for="motor2"></label>
    <span class="pwm-value" id="motor2">{{ motor2Pwm }}</span>
  </div>

  <div class="wrapper" id="motor3-wrapper">
    <label for="motor3"></label>
    <span class="pwm-value" id="motor3">{{ motor3Pwm }}</span>
  </div>

  <div class="wrapper" id="motor4-wrapper">
    <label for="motor4"></label>
    <span class="pwm-value" id="motor4">{{ motor4Pwm }}</span>
  </div>

  <div class="wrapper" id="motor5-wrapper">
    <label for="motor5"></label>
    <span class="pwm-value" id="motor5">{{ motor5Pwm }}</span>
  </div>

  <div class="wrapper" id="motor6-wrapper">
    <label for="motor6"></label>
    <span class="pwm-value" id="motor6">{{ motor6Pwm }}</span>
  </div>

  <div class="wrapper" id="motor7-wrapper">
    <label for="motor7"></label>
    <span class="pwm-value" id="motor7">{{ motor7Pwm }}</span>
  </div>

  <div class="wrapper" id="aileron1-wrapper">
    <label for="aileron1"></label>
    <span class="pwm-value" id="aileron1">{{ aileron1Pwm }}</span>
  </div>

  <div class="wrapper" id="aileron2-wrapper">
    <label for="aileron2"></label>
    <span class="pwm-value" id="aileron2">{{ aileron2Pwm }}</span>
  </div>

  <div class="wrapper" id="rudder">
    <label for="rudder"></label>
    <span class="pwm-value" id="rudder">{{ rudderPwm }}</span>
  </div>

  <div class="wrapper" id="elevator">
    <label for="elevator"></label>
    <span class="pwm-value" id="elevator">{{ elevatorPwm }}</span>
  </div>
</template>
<script setup>
import { ref } from "vue";
let motor1Pwm = ref(0);
let motor2Pwm = ref(0);
let motor3Pwm = ref(0);
let motor4Pwm = ref(0);
let motor5Pwm = ref(0);
let motor6Pwm = ref(0);
let motor7Pwm = ref(0);
let aileron1Pwm = ref(0);
let aileron2Pwm = ref(0);
let rudderPwm = ref(0);
let elevatorPwm = ref(0);
</script>

<style>
#pwm-bg {
  background-image: url("../../../public/albatrossModelLabeled.png");
  background-repeat: no-repeat;
  background-size: 80% 70%;
  background-position: 50% 60%;
}
.wrapper {
  width: 9%;
  height: 10%;
  border-radius: 5px;
  display: none;
}
</style>
