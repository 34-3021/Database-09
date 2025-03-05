<template>
    <div id="head-bar">
        <div id="menu-btn-home" @click="toggleMenu">&#xe7f4;</div>
        <div id="head-title-home"><slot></slot></div>
        <div id="night-btn-home" @click="toggleDarkMode">
            <transition name="fade-anl" mode="out-in"
                ><span v-if="darkModeEnabled" key="moon">&#xe613;</span
                ><span v-else key="sun">&#xe64a;</span></transition
            >
        </div>
    </div>
</template>
<script setup>
import { inject } from "vue";

const toggleMenu = inject("toggleMenu");
const toggleDarkMode = inject("toggleDarkMode");
const darkModeEnabled = inject("darkModeEnabled");
</script>
