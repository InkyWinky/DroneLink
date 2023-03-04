<template>
  <nav>
    <router-link to="/">DroneLink</router-link>
    <!-- <img id="logo-link" src="../public/logolink.png" alt="" /> -->
    <button class="transparentBtn" id="settings-btn">
      <i
        class="fa-sharp fa-solid fa-gears icon-btn-effect"
        id="settings-icon"
      ></i>
    </button>
    <div id="drone-connection">
      <span>Drone Connection</span>
      <div id="connection-status"></div>
    </div>
  </nav>
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
#logo-link {
  height: 2%;
  width: 2%;
  position: absolute;
  left: 51.5%;
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
  padding: 10px;
  margin: 0;
  text-decoration: none;
}

nav a {
  font-weight: normal;
  font-size: 2.5em !important;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: white;
  font-size: 2em;
  -webkit-font-smoothing: antialiased;
}
#settings-icon {
  color: white;
  font-size: 2em;
}
#settings-btn {
  position: absolute;
  left: 20px;
  top: 2%;
}
#drone-connection {
  color: white;
  position: absolute;
  right: 20px;
  top: 1.8%;
  font-family: "Open Sans", sans-serif;
  font-size: 1.5em;
  -webkit-font-smoothing: antialiased;
}
#connection-status {
  background-color: greenyellow;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  margin: 20px;
  margin-top: 16px;
  box-shadow: 0 0 5px 2px greenyellow;
}
</style>
