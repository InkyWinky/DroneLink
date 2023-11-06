<template>
  <div class="flex items-center justify-start ml-20">
    <div
      :id="
        isWebSocketConnected &&
        store?.live_data?.ip &&
        store?.live_data?.ip != 'CONNECT TO MISSION PLANNER'
          ? 'connection-status-on'
          : 'connection-status-off'
      "
    />
    <p
      v-if="!isLoading"
      id="command-btn"
      href="#modal-center"
      uk-toggle
      class="whitespace-nowrap"
    >
      {{
        store.live_data?.ip && isWebSocketConnected
          ? store.live_data?.ip
          : "No Connected MM WebSocket"
      }}
    </p>
    <p
      v-else
      id="command-btn"
      href="#modal-center"
      uk-toggle
      class="whitespace-nowrap"
    >
      LOADING...
    </p>
  </div>

  <div id="modal-center" class="uk-flex-top" uk-modal>
    <div class="uk-modal-dialog uk-modal-body uk-height-max-medium rounded-lg">
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
</template>

<script>
import { useForm } from "vue-hooks-form";
import api from "../api";
import { ref } from "vue";
import { store } from "../store";
// import toggleSettingsMenu from "./store";

export default {
  setup() {
    const connected_ip = ref("");
    const connectionError = ref(false);
    const isLoading = ref(false);
    const isSuccess = ref(false);

    // Connection States
    const isWebSocketConnected = ref(false);

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
      const res = api.executeCommand("CONNECTIP", { ip: ip }).then((res) => {
        console.log("Connect IP: ", { res });
        if (res?.status == 200) {
          document.getElementById("cancel_button").click();
          isSuccess.value = true;
        } else {
          connectionError.value = true;
          setTimeout(() => {
            connectionError.value = false;
          }, 4000);
        }
        isLoading.value = false;
      });
      console.log({ res });
    }

    console.log("[INFO] Starting connection to WebSocket Server");
    // console.log(`ws:${window.location.host.split(":")[0]}:8081`);
    const connection = new WebSocket(
      `ws:${window.location.host.split(":")[0]}:8081`
    );
    connection.onmessage = function (event) {
      event;
      store.updateLiveData(JSON.parse(event.data));
      // console.log("live_data_feed: ", JSON.parse(event.data));
    };
    connection.onopen = function () {
      // console.log(event);
      console.log("[INFO] Successfully connected to the WebSocket server");
      isWebSocketConnected.value = true;
    };
    connection.onclose = function () {
      console.log("[INFO] Disconnected from the WebSocket server");
      isWebSocketConnected.value = false;
    };
    connection.onerror = function (event) {
      console.log(
        "[ERROR] Connection error occured on the WebSocket server",
        event
      );
      isWebSocketConnected.value = false;
    };

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
      isWebSocketConnected,
    };
  },
};
</script>

<style scoped>
#command-btn {
  font-family: "Inter", sans-serif;
  color: white;
  font-size: 1.1em;
}
#command-btn:hover {
  font-weight: bold;
  cursor: pointer;
}
#connection-status-on {
  background-color: greenyellow;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  box-shadow: 0 0 5px 2px greenyellow;
}
#connection-status-off {
  background-color: red;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  float: right;
  box-shadow: 0 0 5px 2px red;
}
</style>
