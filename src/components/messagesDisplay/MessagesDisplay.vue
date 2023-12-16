<template>
  <div class="mb-4 h-[90%] rounded-md">
    <ul
      class="divide-y-[1px] divide-gray-500 h-full bg-gray-200 rounded-md overflow-y-scroll"
    >
      <li
        v-if="store?.messages?.length <= 0"
        class="h-full w-full flex flex-col justify-center items-center"
      >
        No Messages Found!
      </li>
      <li
        v-for="message in store?.messages.slice().reverse()"
        :key="message.time"
        class="flex gap-3 my-2 px-2"
      >
        <p class="italic text-xs w-1/3">{{ message.time }}</p>
        <p class="text-start text-sm w-2/3">{{ message.message }}</p>
      </li>
    </ul>
  </div>
  <p>
    {{ store?.messages.length }}
  </p>
</template>

<script setup>
import { store } from "@/store";
</script>
