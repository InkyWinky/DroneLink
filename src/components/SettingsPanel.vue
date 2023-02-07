<script setup>
import { inject, reactive } from 'vue';


// Since we're toggling whether something should be visible, we inject this data from an outside source
const settingsOpen = inject('settingsOpen');

function toggleSettings() {
    settingsOpen.value = !settingsOpen.value;
}
</script>

<template>
    <div :class="{'uk-open':settingsOpen.value, 'uk-modal':true}" :style="settingsOpen.value ? 'display:block;' : ''" uk-modal>
        <div class="uk-modal-dialog uk-modal-body">
            <button class="uk-modal-close-default" type="button" @click="toggleSettings" uk-close></button>
            <h2 class="uk-modal-title">Settings</h2>
            <p>Here's where you can change your settings</p>
        </div>
    </div>
</template>

<style>
</style>