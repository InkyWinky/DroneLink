<!-- NoteBlock.vue
  [ ] upon load, will show blank note
  [ ] user has option to load previous note
  [ ] each new line will have timestamp
  [ ] user can name note at the top (placeholder = New Note)
-->

<template>
  <Teleport to="body">
    <div v-if="showSaved" class="modal-container" id="panel">
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
            <tr v-for="note in savedNotes" :key="note.id">
              <td class="text-left text-ellipsis overflow-hidden ...">
                <button
                  @click="selectNote(note)"
                  class="uk-button uk-button-primary"
                >
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
        <button @click="newNote()">Create New Note</button>
      </div>
    </div>
  </Teleport>
  <div class="uk-card uk-card-default uk-card-body" id="panel">
    <h3>NOTES</h3>
    <form v-bind:class="selectedNote">
      <input v-model="selectedNote.title" placeholder="New Note" />
    </form>
    <!-- <button @click="loadNotes()">Load Saved Note</button> -->
    <textarea
      v-model="selectedNote.text"
      ref="textarea"
      id="text-input"
      cols="100"
      rows="8"
    ></textarea>
    <button class="uk-button uk-button-primary" @click="saveNote()">
      Save
    </button>
    <button class="uk-button uk-button-primary" @click="loadNotes()">
      Load Notes
    </button>
  </div>
</template>

<script setup>
// import NoteBlock from "./NoteBlock.vue";
import { onMounted, ref } from "vue";

let id = -1;
const blankNote = ref({
  id: id++,
  title: "",
  text: "",
  modifiedDate: new Date().toLocaleTimeString(),
});

const selectedNote = ref({
  id: "",
  title: "",
  text: "",
  modifiedDate: null,
});

onMounted(() => {
  selectedNote.value = blankNote.value;
  console.log("New note initialised");
});

const showSaved = ref(false);

const savedNotes = ref([
  // will be filled with previously saved notes
  {
    id: id++,
    title: "Albatross crashed",
    text: "",
    modifiedDate: new Date().toLocaleDateString(),
    show: false,
  },
  {
    id: id++,
    title: "Albatross achieved hover",
    text: "",
    modifiedDate: new Date().toLocaleDateString(),
    show: false,
  },
]);

// allows user to open a saved note - this opens the modal
function loadNotes() {
  showSaved.value = true;
}

function newNote(currentNote) {
  if (confirm("Save current note?")) {
    saveNote(currentNote);
  }
  selectedNote.value = blankNote.value;
}

/** allows user to create notes */
function saveNote() {
  selectedNote.value.modifiedDate = new Date().toLocaleDateString();
  savedNotes.value.push(selectedNote.value);
  selectedNote.value = blankNote.value; // open note reverts to a blank value for next form submission
}

// eslint-disable-next-line
function selectNote(note) {
  note.show = true;
  selectedNote.value = note;
}

/** allows user to remove notes */
// eslint-disable-next-line
function removeNote(note) {
  if (confirm("Delete note?")) {
    savedNotes.value = savedNotes.value.filter((t) => t !== note);
  }
}

// function saveNote(noteToSave) {
//   selectedNote.value = noteToSave;
//   selectedNote.value.show = false;
//   selectedNote.value.modifiedDate = new Date().toLocaleDateString();
// }

// /* allows user to */
// function clearNote() {
//   selectedNote.value = {
//     id: 0,
//     show: false,
//     title: "",
//     text: "",
//   };
// }
</script>

<style scoped>
div {
  height: 100%;
}
#panel {
  border-radius: 20px;
  width: 100%;
  z-index: 1;
  padding: 20px 10px 20px 10px;
}
#text-input {
  width: 90%;
  height: 85%;
  background-color: #fffeef;
  padding: 0;
  outline: none;
  border-style: none;
}
#open-note-btn {
  position: absolute;
  bottom: 15px;
  right: 55px;
}

#open-note-icon {
  font-size: 2em;
  color: grey;
}

#save-btn {
  position: absolute;
  bottom: 15px;
  right: 15px;
}

#save-icon {
  font-size: 2em;
  color: grey;
}

.time-stamp {
  display: inline-block;
  background-color: grey;
  color: white;
  padding: 2px 5px;
  border-radius: 5px;
  font-size: auto;
  margin-right: 5px;
}

.note-list {
  display: inline-block;
  justify-content: left;
}

.note-table {
  font-size: auto;
}
</style>
