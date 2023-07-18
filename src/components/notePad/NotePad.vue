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
          <!-- <ul>
            <li v-for="line in note" :key="line.line_id">
              {{ line.text }}
            </li>
          </ul> -->
          <button @click="removeNote(note)">X</button>
          <button @click="toggleNote(note)">Open</button>
        </li>
      </ul>
      <form v-bind:class="newNote" @submit.prevent="addNote">
        <input v-model="newNote" placeholder="New note" />
      </form>
    </div>
    <!-- <div class="time-stamp">
      <ul>
        <li v-for="note in notes" :key="note.id">
          <b>{{ note.time }}</b>
        </li>
      </ul>
    </div> -->
  </div>
  <!-- <form v-model="notes.value" @submit.prevent="addLine(note)">
    
  -->
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
import { ref } from "vue";

let id = 0;
let line_id = 0;
const newNote = ref("");

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

/** allows user to remove notes */
function removeNote(note) {
  notes.value = notes.value.filter((t) => t !== note);
}

function toggleNote(note) {
  note.toggle = !note.toggle;
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
