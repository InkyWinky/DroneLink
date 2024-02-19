<template>
  <div class="flex items-center justify-start ml-20">
    <p
      v-if="!isLoading"
      id="command-btn"
      href="#modal-center"
      uk-toggle
      class="whitespace-nowrap"
    >
      {{
        store.live_data?.ip && isWebSocketConnected
          ? `${
              store?.live_data?.ip != "CONNECT TO MISSION PLANNER"
                ? "Mission Planner IP: "
                : ""
            } ${store.live_data?.ip}`
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
    <div
      class="flex-none mx-2"
      :id="
        isWebSocketConnected &&
        store?.live_data?.ip &&
        store?.live_data?.ip != 'CONNECT TO MISSION PLANNER' &&
        store.live_data?.drone_connected
          ? 'connection-status-on'
          : 'connection-status-off'
      "
    />
  </div>

  <div id="modal-center" class="uk-flex-top" uk-modal>
    <div class="uk-modal-dialog uk-modal-body rounded-lg h-fit">
      <button class="uk-modal-close-default" type="button" uk-close></button>
      <div class="h-fit overflow-y-auto">
        <p class="font-bold text-center text-lg">Connections</p>
        <span class="flex w-full items-center">
          <div
            class="flex-none m-2"
            :id="
              isWebSocketConnected
                ? 'connection-status-on'
                : 'connection-status-off'
            "
          />
          <p>Mission Management WebSocket Server</p>
        </span>
        <span class="flex w-full items-center">
          <div
            class="flex-none m-2"
            :id="
              store?.live_data?.ip &&
              store?.live_data?.ip != 'CONNECT TO MISSION PLANNER' &&
              !isLoading
                ? 'connection-status-on'
                : 'connection-status-off'
            "
          />
          <div class="flex">
            <p>Mission Planner Connection</p>
            <p class="text-green-500 pl-2">
              {{
                store?.live_data?.ip &&
                store?.live_data?.ip != "CONNECT TO MISSION PLANNER" &&
                !isLoading
                  ? store.live_data?.ip
                  : ""
              }}
            </p>
          </div>
        </span>
        <span class="flex w-full items-center">
          <div
            class="flex-none m-2"
            :id="
              store.live_data?.drone_connected
                ? 'connection-status-on'
                : 'connection-status-off'
            "
          />
          <p>MAVLINK Connection</p>
        </span>
        <form @submit="onSubmit" class="flex flex-col justify-between">
          <span
            v-show="
              isWebSocketConnected.valueOf() &&
              !(
                store?.live_data?.ip &&
                store?.live_data?.ip != 'CONNECT TO MISSION PLANNER' &&
                !isLoading
              )
            "
            class="p-4 w-full"
          >
            <label class="font-bold text-lg">Connect to Mission Planner</label>
            <input
              v-if="
                !(
                  store?.live_data?.ip &&
                  store?.live_data?.ip != 'CONNECT TO MISSION PLANNER' &&
                  !isLoading
                )
              "
              v-model="ip.value"
              :class="{ 'uk-form-danger': ip.error }"
              :ref="ip.ref"
              :placeholder="ip.value"
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
          </span>
          <span class="flex flex-row-reverse justify-self-end m-0 p-0">
            <button
              v-if="
                !(
                  store?.live_data?.ip &&
                  store?.live_data?.ip != 'CONNECT TO MISSION PLANNER' &&
                  !isLoading
                )
              "
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
  </div>
</template>

<script>
import { useForm } from "vue-hooks-form";
import api from "../api";
import { ref, watch } from "vue";
import { store, fpv_cam, fpv_cam_framerate, vision_cam } from "../store";
// import toggleSettingsMenu from "./store";

export default {
  setup() {
    const connected_ip = ref("");
    const connectionError = ref(false);
    const isLoading = ref(false);
    const isSuccess = ref(false);

    // Connection States
    const isWebSocketConnected = ref(false);
    const lastFPVCamTime = ref(Date.now());
    const newTime = ref();

    watch(isWebSocketConnected, async (value) => {
      // Reset live data if no connection
      if (!value) {
        store.live_data = {};
        isSuccess.value = false;
      }
    });
    const { useField, handleSubmit } = useForm({
      defaultValues: {},
    });
    const localIP = window.location.host.split(":")[0];
    const ip = useField("ip", {
      value: localIP,
      rule: { required: true, min: 7, max: 15 },
    });
    ip.value = localIP;
    let ws_connection = null;
    const connectWebSocket = () => {
      if (!ws_connection) {
        console.log("[INFO] Starting connection to WebSocket Server");
      }
      ws_connection = new WebSocket(
        `ws:${window.location.host.split(":")[0]}:8081`
      );
      ws_connection.onmessage = function (event) {
        event;

        const data = JSON.parse(event.data);
        switch (data.command) {
          case "LIVE_DATA":
            store.updateLiveData(data);
            break;
          case "FPV_CAM":
            newTime.value = Date.now();
            fpv_cam_framerate.value = (
              1000 /
              (newTime.value - lastFPVCamTime.value)
            ).toFixed(0);
            lastFPVCamTime.value = newTime.value;
            fpv_cam.value = data.image;
            break;
          case "VISION_CAM":
            console.log("RECEIVED IMAGE");
            vision_cam.value = data.image;
            break;
          default:
            console.log(
              `[INFO] Received unknown Command from Websocket: ${data.command}`
            );
        }

        // console.log("live_data_feed: ", JSON.parse(event.data));
      };
      ws_connection.onopen = function () {
        // console.log(event);
        console.log("[INFO] Successfully connected to the WebSocket server");
        isWebSocketConnected.value = true;
      };
      ws_connection.onclose = function () {
        console.log(
          "[INFO] Disconnected from the WebSocket server, retrying connection in 1 second..."
        );
        isWebSocketConnected.value = false;
        setTimeout(() => {
          connectWebSocket();
        }, 1000);
      };
      ws_connection.onerror = function (event) {
        console.log(
          "[ERROR] Connection error occured on the WebSocket server, closing connection...",
          event
        );
        isWebSocketConnected.value = false;
        ws_connection.close();
      };
    };

    function connect(ip) {
      // Attempts to connect to a device that is running Mission Planner with the Communication Script.
      // Assumes that the client is already connected to the backend WebSocket Server.
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

    const onSubmit = (data) => connect(data.ip);

    connectWebSocket();

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
  height: 8px;
  width: 8px;
  border-radius: 5px;
  float: right;
  box-shadow: 0 0 5px 2px greenyellow;
}

#connection-status-off {
  background-color: red;
  height: 8px;
  width: 8px;
  border-radius: 5px;
  float: right;
  box-shadow: 0 0 5px 2px red;
}
</style>
