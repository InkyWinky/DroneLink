import { reactive, ref, computed } from "vue";

export const store = reactive({
  live_data: {},
  messages: [],
  updateLiveData(data) {
    if (data["messages"].length > 0) {
      console.log(data["messages"]);
      this.messages = this.messages.concat(data["messages"]);
      data["messages"] = [];
    }
    this.live_data = data;
  },
  settings: { default_alt: 20, takeoff_alt: 20, waypoint_type: 16 },
});
export const menuClosed = ref(false);
export const toggleSettingsMenu = () => (menuClosed.value = !menuClosed.value);
export const MENU_WIDTH = 400;
export const CLOSED_MENU_WIDTH = 0;
export const menuWidth = computed(
  () => `${menuClosed.value ? CLOSED_MENU_WIDTH : MENU_WIDTH}px`
);
