<!-- TO DO:
-  Convert each note into a modal/dialog, where:
- the title of the note is shown in the list, and when clicked opens into a larger, editable document
- this way, only need to save the day date of the note, and don't need to save individual timestamps

TASKS:
  [ ] Implement note modal structure
  [ ] Implement font auto-sizing so note list fits
  [X] Implement creation date
  [X] Implement 'last edited' date (works upon save)
  [ ] Implement note local save (individual note and all notes)
-->
<template>
  <Teleport to="body">
    <!-- use the modal component, pass in the prop -->
    <NoteBlock :show="selectedNote.show" @close="selectedNote.show = false">
      <template #header>
        <h3>{{ selectedNote.title }}</h3>
        <!-- clicking X will not save note, but clicking 'save' will -->
        <button @click="selectedNote.show = false">X</button>
      </template>
      <template #body>
        <textarea
          v-model="selectedNote.text"
          ref="textarea"
          id="text-input"
          cols="30"
          rows="10"
        ></textarea>
      </template>
      <template #footer>
        <button
          class="uk-button uk-button-primary"
          @click="saveNote(selectedNote)"
        >
          Save
        </button>
      </template>
    </NoteBlock>
  </Teleport>
  <div class="uk-card uk-card-default uk-card-body" id="panel">
    <h3 class="text-red-500 font-bold">NOTES</h3>
    <div class="note-list">
      <table class="note-table">
        <thead>
          <td>Title</td>
          <td>Modified</td>
        </thead>
        <tbody>
          <tr v-for="note in notes" :key="note.id">
            <td>
              <button @click="selectNote(note)" class="note-open">
                {{ note.title }}
              </button>
            </td>
            <td>{{ note.modifiedDate }}</td>
            <td><button @click="removeNote(note)">X</button></td>
          </tr>
        </tbody>
      </table>
      <form v-bind:class="newNote" @submit.prevent="addNote">
        <input v-model="newNote" placeholder="New note" />
      </form>
    </div>
  </div>
  <!-- below is kept for posterity, until I am sure that I want to get rid of it !! -->

  <!-- <div class="uk-card uk-card-default uk-card-body" id="panel">
    <h3>NOTES</h3>
    <textarea ref="textarea" id="text-input" cols="30" rows="10"></textarea>
    <button class="transparentBtn" id="open-note-btn">
      <i
        class="fa-solid fa-folder-open icon-btn-effect"
        id="open-note-icon"
      ></i>
    </button>
    <button class="transparentBtn" id="save-btn">
      <i class="fa-solid fa-floppy-disk icon-btn-effect" id="save-icon"></i>
    </button>
  </div> -->
</template>

<script setup>
import NoteBlock from "./NoteBlock.vue";
import { ref } from "vue";

let id = -1; // starts at -1 so note id's start from 0
const newNote = ref("");
const selectedNote = ref({
  id: 0,
  show: false,
  title: "",
  text: "",
});

// array of objects containing each note
const notes = ref([
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

/** allows user to create notes */
function addNote() {
  notes.value.push({
    id: id++,
    title: newNote.value,
    time: new Date().toLocaleString(),
  });
  newNote.value = ""; // reset newNote value for next form submission
}

function selectNote(note) {
  note.show = true;
  selectedNote.value = note;
}

/** allows user to remove notes */
function removeNote(note) {
  notes.value = notes.value.filter((t) => t !== note);
}

function saveNote(noteToSave) {
  selectedNote.value = noteToSave;
  selectedNote.value.show = false;
  selectedNote.value.modifiedDate = new Date().toLocaleDateString();
}

//Tried to add timestamps below but didn't work
// import { ref, onMounted } from "vue";

// export default {
//   setup() {
//     const textarea = ref(null);
//     function addDateStamp(e) {
//       if (e.keyCode === 13) {
//         let txt = document.getElementById("text-input");
//         // check if Enter key is pressed
//         console.log(textarea);
//         const currentDate = new Date();
//         const dateStamp = `[${currentDate.toDateString()} ${currentDate.toLocaleTimeString()}] `;
//         const startPos = textarea.value.selectionStart;
//         const endPos = textarea.value.selectionEnd;
//         // const scrollTop = textarea.value.scrollTop;
//         txt.innerHtml =
//           textarea.value.toString().substring(0, startPos) +
//           dateStamp +
//           textarea.value.toString().substring(endPos, textarea.value.length);
//         // textarea.value.setSelectionRange(
//         //   startPos + dateStamp.length,
//         //   startPos + dateStamp.length
//         // );
//         // textarea.value.scrollTop = scrollTop;
//         // e.preventDefault();
//         txt.innerHTML = "hi";
//       }
//     }
//     onMounted(() => {
//       if (textarea.value) {
//         textarea.value.addEventListener("keydown", addDateStamp);
//       }
//     });
//     return { textarea };
//   },
// };
</script>

<style>
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
