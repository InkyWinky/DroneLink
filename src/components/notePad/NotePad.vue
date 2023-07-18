<!-- TO DO:
-  Convert each note into a modal/dialog, where:
- the title of the note is shown in the list, and when clicked opens into a larger, editable document
- this way, only need to save the day date of the note, and don't need to save individual timestamps

TASKS:
  [ ] Implement note modal structure
  [ ] Implement creation date
  [ ] Implement 'last edited' date
  [ ] Implement note local save (individual note and all notes)
-->
<template>
  <div class="uk-card uk-card-default uk-card-body" id="panel">
    <h3>NOTES</h3>
    <div class="note-text">
      <ul>
        <li v-for="note in notes" :key="note.id">
          {{ note.title }} {{ note.Date }}
          <button @click="removeNote(note)">X</button>
          <button @click="showNote = true">Open</button>
          <Teleport to="body">
            <!-- use the modal component, pass in the prop -->
            <NoteBlock :show="showNote" @close="showNote = false">
              <template #header>
                <h3>{{ note.title }}</h3>
              </template>
              <template #body>
                <ul>
                  <li v-for="line in note.text" :key="line.line_id">
                    {{ line.text }}
                  </li>
                </ul>
              </template>
              <template #footer>
                <form v-bind:class="newLine" @submit.prevent="addLine(note)">
                  <input v-model="newLine" placeholder="New line" />
                </form>
                <button @click="saveNote()">Save</button>
              </template>
            </NoteBlock>
          </Teleport>
        </li>
      </ul>
      <form v-bind:class="newNote" @submit.prevent="addNote">
        <input v-model="newNote" placeholder="New note" />
      </form>
    </div>
  </div>
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

let id = 0;
let line_id = 0;
const newNote = ref("");
const newLine = ref("");
const showNote = ref(false);

// array of objects containing each note, which itself contains multiple lines
const notes = ref([
  {
    id: id++,
    title: "Albatross crashed",
    text: [
      {
        line_id: line_id++,
        text: "Albatross suffered motor failure",
        time: new Date().toLocaleTimeString(),
      },
      {
        line_id: line_id++,
        text: "Failure caused it to lean and stall",
        time: new Date().toLocaleTimeString(),
      },
    ],
    time: new Date().toLocaleDateString(),
    show: false,
  },
  {
    id: id++,
    title: "Albatross achieved hover",
    text: [
      {
        line_id: line_id++,
        text: "The Albatross achieved hover today - held stable for 10 seconds before landing.",
        time: new Date().toLocaleTimeString(),
      },
    ],
    time: new Date().toLocaleString(),
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

function addLine(note) {
  note.text.push({
    id: line_id++,
    text: newLine.value,
    time: new Date().toLocaleTimeString(),
  });
  newLine.value = "";
}

/** allows user to remove notes */
function removeNote(note) {
  notes.value = notes.value.filter((t) => t !== note);
}

function saveNote() {
  showNote.value = false;
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
  font-size: 0.8em;
  margin-right: 5px;
}

.note-text {
  display: inline-block;
  justify-content: left;
}
</style>
