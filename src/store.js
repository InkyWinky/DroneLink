import { reactive, ref, computed } from "vue";

export const store = reactive({
  live_data: {
    albatross: {
      ground_height: 0,
      velocity: 0,
    },
    payload: {
      height: 0,
      velocity: 0,
    },
  },
  messages: [],
  updateLiveData(data) {
    if (data["messages"].length > 0) {
      console.log("MESSAGES" + data["messages"]);
      this.messages = this.messages.concat(data["messages"]);
      data["messages"] = [];
    }
    this.live_data = data;
  },
  settings: {
    default_alt: 80,
    takeoff_alt: 50,
    waypoint_type: 16,
    vtol_transition_mode: 4,
  },
});
export const fpv_cam = ref();
export const fpv_cam_framerate = ref(0);
export const vision_cam = ref();
export const menuClosed = ref(false);
export const toggleSettingsMenu = () => (menuClosed.value = !menuClosed.value);
export const MENU_WIDTH = 400;
export const CLOSED_MENU_WIDTH = 0;
export const vision_on = ref(false);
export const menuWidth = computed(
  () => `${menuClosed.value ? CLOSED_MENU_WIDTH : MENU_WIDTH}px`
);
export const debug_mode = ref(true);
