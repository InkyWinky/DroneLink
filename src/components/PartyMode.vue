<template>
  <!-- <button
    uk-toggle="target: #my-id"
    class="uk-button uk-button-primary justify-center w-full bg-gradient-to-r from-red-600 to-violet-900"
    type="button"
  >
    <p class="text-bold text-white">Party Mode?</p>
  </button> -->

  <button class="uk-offcanvas-close relative w-[100%] ml-3 mb-2">
    <button
      @click="togglePopup"
      class="uk-button uk-button-primary justify-center w-full bg-gradient-to-r from-red-600 to-violet-900"
      type="button"
    >
      <p class="text-bold text-white">
        {{ isOpen ? "Close Party Mode?" : "Party Mode?" }}
      </p>
    </button>
  </button>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="absolute top-0 left-0 w-full h-full z-[999999] overflow-hidden"
    >
      <div class="bg-gray-800 opacity-50 w-full h-full z-[999999]"></div>
      <div
        class="absolute top-0 right-0 cursor-pointer z-[999]"
        @click="
          () => {
            isOpen = false;
          }
        "
      >
        <div
          uk-icon="icon:close; ratio: 2"
          class="text-white hover:text-gray-200"
        />
      </div>
      <div class="absolute top-0 left-0 w-full h-full">
        <div class="w-full h-full flex flex-col items-center justify-center">
          <img :src="img" class="w-3/4 rounded-xl outline outline-black" />
          <div
            class="p-1 bg-gray-300 rounded-b-lg text-center outline outline-black font-bold text-black"
          >
            08/01/2024
          </div>
        </div>
      </div>
      <div ref="playground" class="absolute top-0 left-0 w-full h-full">
        <!-- <div class="absolute bg-red-600 rounded-full w-5 h-5" /> -->
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from "vue";
import p from "/public/🤖.json";
const img = ref("data:image/jpg;base64," + p.p1);
const playground = ref();
const isOpen = ref(false);
const togglePopup = () => {
  isOpen.value = !isOpen.value;
};

let confettis = [];
let lights = [];
const FPS = 60;
const G = -1000; // px per second for gravity
const G_2 = -250; // px per second for gravity of person
const MAX_CONFETTI = 15; // the maximum number of confetti/person entities
const MAX_LIGHTS = 4; // the maximum number of lights

const createLight = () => {
  let light = {
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    maxLife: 1000 + Math.random() * 100, // Max life before deleting light in ms
    life: 0,
    delete: false,
    element: undefined,
    update: function () {
      // Delete light condition
      if (this.life >= this.maxLife) {
        this.delete = true;
      }
      this.life += 1000 / FPS;
    },
  };
  light.element = document.createElement("div");
  light.element.style.position = "absolute";
  light.element.style.bottom = `${light.y}px`;
  light.element.style.left = `${light.x}px`;
  light.element.style.width = "5rem";
  light.element.style.height = "5rem";
  light.element.style.backgroundColor = getColor();
  light.element.style.opacity = 0.4;
  light.element.style.filter = "blur(16px)";
  lights.push(light);
  // console.log("Light Created", light);
};

const createConfetti = () => {
  let confetti = {
    x: window.innerWidth / 2,
    y: 0,
    v_x: (Math.random() > 0.5 ? -1 : 1) * 500,
    v_y: 100 + Math.random() * 1500,
    maxLife: 5000, // Max life before deleting confetti in ms
    a: G,
    life: 0,
    delete: false,
    element: undefined,
    update: function () {
      if (this.element) {
        // Delete confetti conditions
        if (
          this.life >= this.maxLife ||
          this.x < 0 ||
          this.y < 0 ||
          this.x > window.innerWidth - 50
        ) {
          this.delete = true;
          return;
        }
        // Confetti Physics
        let t = 1 / FPS;
        this.v_y = this.v_y + this.a * t;
        this.x = this.x + this.v_x * t;
        this.y = this.y + this.v_y * t + (this.a / 2) * t * t;
        this.element.style.bottom = `${this.y}px`;
        this.element.style.left = `${this.x}px`;
        this.life += 1000 / FPS;
      }
    },
  };
  confetti.element = document.createElement("div");
  confetti.element.style.backgroundColor = `${getColor()}`; // random confetti colour
  confetti.element.style.position = "absolute";
  confetti.element.style.bottom = `${confetti.y}px`;
  confetti.element.style.left = `${confetti.x}px`;
  // confetti.element.style.borderRadius = "9999px";
  confetti.element.style.transform = `rotate(${Math.random() * 180}deg)`;
  confetti.element.style.width = "0.5rem";
  confetti.element.style.height = "1rem";

  // Random person confetti
  if (Math.random() < 0.05) {
    confetti.element.innerHTML = `<img src="${
      "data:image/jpg;base64," + getRandomPic()
    }"/>`;
    confetti.element.style.backgroundColor = "";
    confetti.element.style.width = "50px";
    confetti.element.style.height = "50px";
    confetti.element.style.transform = "";
    confetti.a = G_2;
    confetti.v_x = (Math.random() > 0.5 ? -1 : 1) * 100;
    confetti.v_y = 300 + Math.random() * 200;
  }

  confettis.push(confetti);
  // console.log("Confetti Created", confetti);
};

function getColor() {
  return (
    "hsl(" +
    360 * Math.random() +
    "," +
    (50 + 70 * Math.random()) +
    "%," +
    (50 + 10 * Math.random()) +
    "%)"
  );
}

const getRandomPic = () => {
  let choice = Math.round(Math.random() * 3);
  switch (choice) {
    case 0:
      return p.p2;
    case 1:
      return p.p3;
    case 2:
      return p.p4;
    case 3:
      return p.p5;
  }
};

const update = () => {
  if (!isOpen.value) {
    return;
  }
  if (confettis.length <= MAX_CONFETTI) {
    createConfetti();
  }
  if (lights.length <= MAX_LIGHTS) {
    createLight();
  }
  playground.value.innerHTML = "";
  confettis = confettis.filter((c) => !c.delete); // remove deleted confetti
  confettis.forEach((confetti) => {
    confetti.update();
    playground.value.appendChild(confetti.element);
  });

  lights = lights.filter((c) => !c.delete); // remove deleted lights
  lights.forEach((light) => {
    light.update();
    playground.value.appendChild(light.element);
  });
};

onMounted(() => {
  setInterval(() => {
    update();
  }, 1000 / FPS);
});
</script>
