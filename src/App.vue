<template>
  <nav>
    <p id="command-btn" href="#modal-center" uk-toggle>
      {{
        store.live_data?.ip
          ? "IP: " + store.live_data?.ip
          : "Connect to Mission Planner"
      }}
    </p>
    <!-- <router-link to="/" class="flex flex-row items-center justify-center">
      <img src="../public/logo.png" class="h-10" />
      <p class="text-white">DroneLink</p>
    </router-link> -->
    <a href="/" class="flex flex-row items-center justify-center">
      <img src="../public/logo.png" class="h-10" />
      <p class="text-white">DroneLink</p>
    </a>
    <div id="modal-center" class="uk-flex-top" uk-modal>
      <div
        class="uk-modal-dialog uk-modal-body uk-height-max-medium rounded-lg"
      >
        <button class="uk-modal-close-default" type="button" uk-close></button>
        <form @submit="onSubmit" class="h-full flex flex-col justify-between">
          <span class="p-4 w-full">
            <label class="font-bold text-lg">Connect to Mission Planner</label>
            <input
              v-if="!isSuccess.valueOf()"
              v-model="ip.value"
              :class="{ 'uk-form-danger': ip.error }"
              :ref="ip.ref"
              placeholder="Input Ip address of device with Mission Planner"
              class="uk-input"
            />
            <div
              v-if="isLoading.valueOf()"
              uk-spinner
              class="w-full flex flex-col justify-center items-center"
            ></div>
            <p v-if="ip.error" class="text-red-500">
              {{ ip.error.message }}
            </p>
            <p v-if="connectionError.valueOf()" class="text-red-500">
              Connection Failed, Please try again...
            </p>
            <p v-if="isSuccess.valueOf()" class="text-green-500">
              Connection to {{ store?.live_data.ip }} was Successful!
            </p>
          </span>
          <span class="flex flex-row-reverse justify-self-end m-0 p-0">
            <button
              v-if="!isSuccess.valueOf()"
              class="uk-button uk-button-primary bg-blue-600 hover:bg-blue-700 ml-2 mt-2 border-gray-600"
              type="submit"
            >
              Submit
            </button>
            <button
              id="cancel_button"
              class="uk-button uk-button-default uk-modal-close bg-gray-400 hover:bg-gray-500 border-gray-600 text-white mx-2 mt-2"
              type="button"
            >
              Cancel
            </button>
          </span>
        </form>
      </div>
    </div>
    <div id="drone-connection">
      <span
        uk-icon="refresh"
        class="pr-2 cursor-pointer"
        @click="onRefreshClick()"
      ></span>
      <span>Drone Connection</span>
      <div
        :id="
          store.live_data?.drone_connected
            ? 'connection-status-on'
            : 'connection-status-off'
        "
      ></div>
    </div>
  </nav>
  <SettingsMenu />
  <router-view></router-view>
</template>

<script>
import { useForm } from "vue-hooks-form";
import api from "./api";
import { ref } from "vue";
import { store } from "./store";
import SettingsMenu from "./components/settingsMenu/SettingsMenu.vue";
// import toggleSettingsMenu from "./store";

export default {
  setup() {
    const connected_ip = ref("");
    const connectionError = ref(false);
    const isLoading = ref(false);
    const isSuccess = ref(false);
    const { useField, handleSubmit } = useForm({
      defaultValues: {},
    });
    const ip = useField("ip", {
      rule: { required: true, min: 7, max: 15 },
    });

    function connect(ip) {
      console.log("ip is: " + ip);
      connected_ip.value = ip;
      connectionError.value = false;
      isLoading.value = true;
      api.executeCommand("CONNECTIP", { ip: ip }).then((res) => {
        console.log({ res });
        if (res.status == 200) {
          document.getElementById("cancel_button").click();
          isSuccess.value = true;
        } else if (res.status == 400) {
          connectionError.value = true;
          setTimeout(() => {
            connectionError.value = false;
          }, 4000);
        }
        isLoading.value = false;
      });
    }
    const onSubmit = (data) => connect(data.ip);
    return {
      ip,
      connected_ip,
      onSubmit: handleSubmit(onSubmit),
      store,
      // toggleSettingsMenu,
      connectionError,
      isLoading,
      isSuccess,
    };
  },
  created() {
    console.log("Starting connection to WebSocket Server");
    // console.log(`ws:${window.location.host.split(":")[0]}:8081`);
    this.connection = new WebSocket(
      `ws:${window.location.host.split(":")[0]}:8081`
    );
    this.connection.onmessage = function (event) {
      event;
      store.updateLiveData(JSON.parse(event.data));
      // console.log("live_data_feed: ", JSON.parse(event.data));
    };
    this.connection.onopen = function (event) {
      console.log(event);
      console.log("Successfully connected to the websocket server...");
    };
  },
  methods: {
    onRefreshClick() {
      console.log("SYNC SCRIPT button pressed");
      api.executeCommand("SYNC_SCRIPT", {});
    },
  },
  components: { SettingsMenu },
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
#command-btn {
  font-family: "Inter", sans-serif;
  color: white;
  font-size: 1.1em;
  position: absolute;
  left: 6%;
  top: 2%;
}
#command-btn:hover {
  font-weight: bold;
  cursor: pointer;
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
