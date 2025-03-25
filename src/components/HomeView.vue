<template>
    <div id="home-view">
        <Menu id="menu" :curPage="currentPage"></Menu>

        <transition name="fade-anl" mode="out-in"
            ><component :is="curcomponent" ref="copn"></component
        ></transition>
    </div>
</template>
<script setup>
import Menu from "./Menu.vue";
import { onMounted, ref, inject, provide, shallowRef } from "vue";
import Chat from "./Chat.vue";
import Settings from "./Settings.vue";
import Papers from "./Papers.vue";

const menuOn = ref(false);

const copn = ref(null);

const curcomponent = shallowRef(null);

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
provide("toggleMenu", toggleMenu);
provide("Projects", copn);
const toggleDarkModeParent = inject("toggleDarkMode");
const currentPage = ref("");
const switchPage = (page) => {
    currentPage.value = page;
    if (page === "Chat") {
        curcomponent.value = Chat;
    } else if (page === "Papers") {
        curcomponent.value = Papers;
    } else if (page === "Settings") {
        curcomponent.value = Settings;
    }
};
provide("switchPage", (page) => switchPage(page));

const toggleDarkMode = () => {
    toggleDarkModeParent();
};

onMounted(() => {
    currentPage.value = "Chat";
    curcomponent.value = Chat;
});
</script>
