<template>
  <NavBar />
  <router-view></router-view>
</template>

<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;
#app {
  font-family: "Aldrich", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100%;
}
html {
  height: 100%;
}
body {
  height: 100%;
  overflow-y: hidden;
  margin: 0;
  background-color: black;
}
</style>
