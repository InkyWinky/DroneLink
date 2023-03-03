<template>
  <nav><router-link to="/">DroneLink</router-link></nav>
  <router-view />
</template>

<style>
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
  margin: 0;
}
nav {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
  padding: 15px;
  margin: 0;
  text-decoration: none;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: white;
  font-size: 2em;
}
</style>
