import { reactive } from "vue";

export const store = reactive({
  live_data: {},
  updateLiveData(data) {
    this.live_data = data;
  },
});
