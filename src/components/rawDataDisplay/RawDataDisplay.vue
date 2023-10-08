<template>
  <div class="mb-4 h-[90%] rounded-md">
    <ul
      class="divide-y-[1px] divide-gray-500 h-full bg-gray-200 rounded-md overflow-y-scroll"
    >
      <li
        v-for="key in Object.keys(store?.live_data)"
        :key="key"
        class="flex gap-3 my-2 px-2"
      >
        <p class="italic text-xs w-1/3">{{ key }}</p>
        <p class="text-end text-sm w-2/3">
          {{
            typeof store?.live_data[key] == "number"
              ? store?.live_data[key].toFixed(4)
              : store?.live_data[key]
          }}
        </p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { store } from "@/store";
</script>
