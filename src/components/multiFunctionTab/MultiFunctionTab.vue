<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 20px; padding: 20px"
  >
    <div class="w-full overflow-x-auto h-fit">
      <ul class="uk-tab w-max" uk-tab>
        <li v-for="t in tabs" :key="t.name" @click="setTab(t.name)">
          <a href="#"> {{ t.name }} </a>
        </li>
      </ul>
    </div>

    <span v-for="t in tabs" :key="t.name" class="font-normal">
      <component
        class="h-[90%]"
        v-if="tab.valueOf() == t.name"
        :is="() => t.component"
      />
    </span>
    <!-- <div v-if="tab.valueOf() == 'Notes'" class="h-[90%]">
      <NotePad_new />
    </div>
    <div v-else-if="tab.valueOf() == 'Messages'" class="h-[90%]">
      <RawDataDisplay />
    </div> -->
  </div>
</template>

<script setup>
import MessagesDisplay from "@/components/messagesDisplay/MessagesDisplay.vue";
import NotePad_new from "@/components/notePad/NotePad_new.vue";
import RawDataDisplay from "@/components/rawDataDisplay/RawDataDisplay.vue";
import { ref } from "vue";
const tabs = [
  { name: "Notes", component: <NotePad_new /> },
  { name: "Messages", component: <MessagesDisplay /> },
  { name: "Raw Data", component: <RawDataDisplay /> },
];
let tab = ref("Notes");

const setTab = (tabName) => {
  tab.value = tabName;
};
</script>
