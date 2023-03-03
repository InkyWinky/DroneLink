<template>
  <nav>
    <router-link to="/">DroneLink</router-link>
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
