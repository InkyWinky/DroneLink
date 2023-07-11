<script setup>
import { ref } from "vue";

let id = 0;
const newNote = ref("");

// array of objects containing each note, which itself contains multiple lines
const notes = ref([
  // { id: id++, text: "Albatross crashed", time: new Date().toLocaleString() },
  // { id: id++, text: "Albatross achieved hover", time: new Date().toLocaleString() }
]);

/** allows user to create notes */
function addNote() {
  notes.value.push({
    id: id++,
    text: newNote.value,
    time: new Date().toLocaleString(),
  });
  newNote.value = "";
}

/** allows user to remove notes */
function removeNote(note) {
  notes.value = notes.value.filter((t) => t !== note);
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

<template>
  <ul>
    <li v-for="note in notes" :key="note.id">
      {{ note.text }}
      <button @click="removeNote(note)">X</button>
      {{ note.time }}
    </li>
  </ul>
  <form :class="newNote" @submit.prevent="addNote">
    <input v-model="newNote" placeholder="New note" />
  </form>
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
</style>
