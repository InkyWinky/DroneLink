<template>
  <nav>
    <router-link to="/">DroneLink</router-link>
    <!-- <img id="logo-link" src="../public/logolink.png" alt="" /> -->
    <button class="transparentBtn" id="settings-btn">
      <i class="fa-sharp fa-solid fa-gears icon-btn-effect" id="settings-icon">
      </i>
    </button>
    <a class="uk-button uk-button-default" href="#modal-center" uk-toggle
      >Connect to Mission Planner</a
    >

    <div id="modal-center" class="uk-flex-top" uk-modal>
      <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
        <button class="uk-modal-close-default" type="button" uk-close></button>

        <form @submit="onSubmit">
          <label>Input IP address of device with Mission Planner:</label>
          <input v-model="ip.value" :ref="ip.ref" />
          <p v-if="ip.error">{{ ip.error.message }}</p>
          <button type="submit">submit</button>
        </form>
      </div>
    </div>
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
<script>
import { useForm } from "vue-hooks-form";
import api from "./api";
export default {
  setup() {
    const { useField, handleSubmit } = useForm({
      defaultValues: {},
    });
    const ip = useField("ip", {
      rule: { required: true, min: 7, max: 15 },
    });
    function connect(ip) {
      console.log("ip is: " + ip);
      api.executeCommand("CONNECTIP", { ip: ip });
    }
    const onSubmit = (data) => connect(data.ip);
    return {
      ip,
      onSubmit: handleSubmit(onSubmit),
    };
  },
};
</script>
