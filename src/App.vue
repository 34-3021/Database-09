<template>
    <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
            <component :is="Component" />
        </transition>
    </router-view>
</template>
<script setup>
import { ref, watch, provide, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const loginState = ref({ loggedIn: false });

const darkModeEnabled = ref(false);

const toggleDarkMode = () => {
    darkModeEnabled.value = !darkModeEnabled.value;
    document.documentElement.classList.toggle("dark-mode");
};
provide("toggleDarkMode", toggleDarkMode);
provide("darkModeEnabled", darkModeEnabled);

//watch(loginState, checkLoginState, { immediate: true });

onMounted(() => {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        if (!darkModeEnabled.value) {
            toggleDarkMode();
        }
    }
});
</script>
