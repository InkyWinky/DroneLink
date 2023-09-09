<template>
  <div
    class="uk-card uk-card-default uk-card-body"
    style="border-radius: 20px; padding: 20px"
  >
    <ul>
      <ul class="uk-tab" uk-tab>
        <li class="uk-active" @click="setTab('notepad')">
          <a href="#"> Notes </a>
        </li>
        <li @click="setTab('messages')">
          <a href="#"> Messages </a>
        </li>
      </ul>
    </ul>
    <div v-if="tab.valueOf() == 'messages'" class="h-full">
      <MessagesDisplay />
    </div>
    <div v-else-if="tab.valueOf() == 'notepad'" class="h-[90%]">
      <NotePad_new />
    </div>
  </div>
</template>

<script setup>
import MessagesDisplay from "@/components/messagesDisplay/MessagesDisplay.vue";
import NotePad_new from "@/components/notePad/NotePad_new.vue";
import { ref } from "vue";

let tab = ref("notepad");

const setTab = (tabName) => {
  tab.value = tabName;
};
</script>
