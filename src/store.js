import { reactive, ref, computed } from "vue";

export const store = reactive({
  live_data: {},
  updateLiveData(data) {
    this.live_data = data;
  },
});
export const menuClosed = ref(false);
export const toggleSettingsMenu = () => (menuClosed.value = !menuClosed.value);
export const MENU_WIDTH = 400;
export const CLOSED_MENU_WIDTH = 0;
export const menuWidth = computed(
  () => `${menuClosed.value ? CLOSED_MENU_WIDTH : MENU_WIDTH}px`
);
