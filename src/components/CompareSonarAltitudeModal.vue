<template>
  <div
    v-if="AltSonarDiscrepancy"
    id="alt-sonar-discrepancy"
    class="uk-alert-warning"
    uk-alert
  >
    <a href class="uk-alert-close" uk-close></a>
    <p>
      Warning: Sonar (LiDAR) Range ({{ store?.live_data?.sonarrange }}) is
      different to estimated altidude ({{ store?.live_data?.alt }})
    </p>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { store } from "@/store";

const AltSonarDiscrepancy = ref(false);
const checkAltSonarDiscrepancy = ref(true);

function absoluteVal(val) {
  if (val < 0) {
    return val * -1;
  } else return val;
}

// check discrepancy b/n sonar range and altitude every 5 sec
async function compareAltToSonar() {
  while (checkAltSonarDiscrepancy.value) {
    await setTimeout(() => {
      AltSonarDiscrepancy.value =
        absoluteVal(store?.live_data?.sonarrange - store?.live_data?.alt) >= 10;
    }, 5000);
  }
}

compareAltToSonar();
</script>

<styles>
</styles>
