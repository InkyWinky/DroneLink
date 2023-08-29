<template>
  <div v-if="props.show" class="modal-container" id="panel">
    <div class="modal-header">
      <h3 class="font-bold">NOTES</h3>
    </div>
    <div class="modal-body">
      <table class="table-fixed">
        <thead>
          <td>Title</td>
          <td>Date Modified</td>
        </thead>
        <tbody>
          <tr v-for="note in NotePad.savedNotes" :key="note.id">
            <td class="text-left text-ellipsis overflow-hidden ...">
              <button @click="selectNote(note)" class="note-open">
                {{ note.title }}
              </button>
            </td>
            <td class="text-sm">{{ note.modifiedDate }}</td>
            <td><button @click="removeNote(note)">X</button></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="modal-footer">
      <!-- <form v-bind:class="newNote" @submit.prevent="addNote">
        <input v-model="newNote" placeholder="New note" />
      </form> -->
      <button @click="newNote()">Create New Note</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";
import NotePad from "./NotePad.vue";
const props = defineProps({
  show: Boolean,
});
</script>

<style></style>
