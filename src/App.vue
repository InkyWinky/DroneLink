<template>
  <nav>
    <div class="flex w-full items-center">
      <div class="w-1/3"></div>

      <router-link
        to="/"
        class="flex flex-row w-1/3 items-center justify-center"
      >
        <img src="../public/logo.png" class="h-10" />
        <p class="text-white">DroneLink</p>
      </router-link>
      <div class="w-1/3 flex justify-end">
        <ConnectionStatus />
      </div>
    </div>

    <!-- <div id="drone-connection">
      <span
        uk-icon="refresh"
        class="pr-2 cursor-pointer"
        @click="onSyncDrone()"
      ></span>
      <span>Drone Connection</span>
      <div
        :id="
          store.live_data?.drone_connected
            ? 'connection-status-on'
            : 'connection-status-off'
        "
      ></div>
    </div> -->
  </nav>
  <SettingsMenu />
  <router-view></router-view>
</template>

<script>
import { store } from "./store";
import { api } from "./api";
import SettingsMenu from "./components/settingsMenu/SettingsMenu.vue";
import ConnectionStatus from "./components/ConnectionStatus.vue";
// import toggleSettingsMenu from "./store";

export default {
  setup() {
    return { store, api };
  },
  components: { SettingsMenu, ConnectionStatus },
  // methods: {
  //   onSyncDrone() {
  //     console.log("[ACTION] SYNC SCRIPT button pressed");
  //     api.executeCommand("SYNC_SCRIPT", {});
  //   },
  // },
};
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
.connect-btn {
  font-size: 1em !important;
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
  overflow-y: hidden;
  margin: 0;
  background-color: #eeeeee;
}
nav {
  background: linear-gradient(0.25turn, #79d9ff, #9198e5);
  padding: 5px;
  margin: 0;
  text-decoration: none;
}

nav a {
  font-weight: normal;
  font-size: 2.5em;
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
  font-size: 1.5em;
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
#connection-status-on {
  background-color: greenyellow;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  margin: 20px;
  margin-top: 16px;
  box-shadow: 0 0 5px 2px greenyellow;
}
#connection-status-off {
  background-color: red;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  margin: 20px;
  margin-top: 16px;
  box-shadow: 0 0 5px 2px red;
}
</style>
