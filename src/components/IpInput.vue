<template>
  <a class="uk-button uk-button-default" href="#modal-center" uk-toggle>{{
    connected_ip.valueOf()
      ? "IP: " + connected_ip.valueOf()
      : "Connect to Mission Planner"
  }}</a>

  <div id="modal-center" class="uk-flex-top" uk-modal>
    <div class="uk-modal-dialog uk-modal-body uk-height-max-medium rounded-lg">
      <button class="uk-modal-close-default" type="button" uk-close></button>
      <form @submit="onSubmit" class="h-full flex flex-col justify-between">
        <span class="p-4 w-full">
          <label class="font-bold text-lg">Hello banan</label>
          <input
            v-model="ip.value"
            :class="{ 'uk-form-danger': ip.error }"
            :ref="ip.ref"
            placeholder="InHello Bannana"
            class="uk-input"
          />
          <p v-if="ip.error" class="text-red-500">
            {{ ip.error.message }}
          </p>
        </span>
        <span class="flex flex-row-reverse justify-self-end m-0 p-0">
          <button
            class="uk-button uk-button-primary bg-blue-600 hover:bg-blue-700 ml-2 mt-2 border-gray-600"
            type="submit"
          >
            Submit
          </button>
          <button
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
    <span>Drone Connection</span>
    <div id="connection-status"></div>
  </div>
</template>

<script>
import { useForm } from "vue-hooks-form";
import api from "./../api";
import { ref } from "vue";
export default {
  setup() {
    const connected_ip = ref("");
    const { useField, handleSubmit } = useForm({
      defaultValues: {},
    });
    const ip = useField("ip", {
      rule: { required: true, min: 7, max: 15 },
    });
    function connect(ip) {
      console.log("ip is: " + ip);
      connected_ip.value = ip;
      api.executeCommand("CONNECTIP", { ip: ip });
    }
    const onSubmit = (data) => connect(data.ip);
    return {
      ip,
      connected_ip,
      onSubmit: handleSubmit(onSubmit),
    };
  },
};
</script>
