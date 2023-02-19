<template>
  <div class="home">
    <WaypointsList />
  </div>
</template>

<script>
// @ is an alias to /src

import WaypointsList from "@/components/waypoints/WaypointsList.vue";
export default {
  name: "HomeView",
  components: {
    WaypointsList,
  },
};
</script>
<style>
body {
  background-color: #eeeeee;
  height: 100%;
}
div {
  height: 100%;
}
</style>
