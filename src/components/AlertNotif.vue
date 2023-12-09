<template>
  <div id="alert-container" class="fade-in">
    {{ alertMessage }}
  </div>
</template>

<script setup>
defineProps({
  alertMessage: String,
});
</script>

<style scoped>
#alert-container {
  position: absolute;
  bottom: 10px;
  padding: 20px;
  background-color: rgba(13, 9, 65, 0.97);
  border-radius: 5px;
  color: white;
  z-index: 999;
  left: 10px;
}

.fade-in {
  opacity: 0;
  animation-name: fadeInOpacity;
  animation-iteration-count: 1;
  animation-timing-function: ease-in-out;
  animation-duration: 3s;
}

@keyframes fadeInOpacity {
  0% {
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>
