<template>
  <a class="uk-button-mini uk-button-default connect-btn" uk-toggle
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
</template>
<script>
import { useForm } from "vue-hooks-form";
export default {
  setup() {
    const { useField, handleSubmit } = useForm({
      defaultValues: {},
    });
    const ip = useField("ip", {
      rule: { required: true, min: 7, max: 15 },
    });
    const onSubmit = (data) => console.log(data);
    return {
      ip,
      onSubmit: handleSubmit(onSubmit),
    };
  },
};
</script>
