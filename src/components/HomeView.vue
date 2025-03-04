<template>
    <div id="home-view">
        <Menu id="menu"></Menu>
        <div id="home-main">
            <div id="main-left">s</div>
            <div id="main-main">
                <div id="head-bar">
                    <div id="menu-btn-home" @click="toggleMenu">&#xe7f4;</div>
                    <div id="head-title-home">InfiniDoc 对话</div>
                    <div id="night-btn-home" @click="toggleDarkMode">
                        &#xe7f4;
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import Menu from "./Menu.vue";

import { RouterLink } from "vue-router";
import NotLoggedInMenu from "./NotLoggedInMenu.vue";
import { onMounted, ref, inject } from "vue";

const menuOn = ref(false);
const toggleMenu = () => {
    if (menuOn.value) {
        document.getElementById("menu").style.marginLeft =
            "-" + document.getElementById("menu").offsetWidth + "px";
        menuOn.value = false;
    } else {
        document.getElementById("menu").style.marginLeft = "0";
        menuOn.value = true;
    }
};
const toggleDarkModeParent = inject("toggleDarkMode");

const toggleDarkMode = () => {
    toggleDarkModeParent();
};
</script>
