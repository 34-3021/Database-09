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
import { BACKEND_BASE_URL, WEBSOCKET_URL } from "./components/endpoints";

const loginState = ref({ loggedIn: false });

const darkModeEnabled = ref(false);

const router = useRouter();

const toggleDarkMode = () => {
    darkModeEnabled.value = !darkModeEnabled.value;
    document.documentElement.classList.toggle("dark-mode");
};
provide("toggleDarkMode", toggleDarkMode);
provide("darkModeEnabled", darkModeEnabled);

provide("loginState", loginState);

//watch(loginState, checkLoginState, { immediate: true });

const verifyInfiniDocToken = (token) => {
    return new Promise((resolve, reject) => {
        fetch(BACKEND_BASE_URL + "/login/verifyToken", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token: token }),
        })
            .then((res) => res.json())
            .then((res) => {
                if (res.success) {
                    resolve({
                        status: true,
                        message: "已读取 InfiniDoc Token",
                    });
                } else {
                    resolve({
                        status: false,
                        message: "InfiniDoc Token 无效",
                    });
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
};

onMounted(() => {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        if (!darkModeEnabled.value) {
            toggleDarkMode();
        }
    }
    //check if infinidoc_token is set
    if (localStorage.getItem("infinidoc_token")) {
        verifyInfiniDocToken(localStorage.getItem("infinidoc_token")).then(
            (res) => {
                if (res.status) {
                    loginState.value.loggedIn = true;
                    loginState.value.token =
                        localStorage.getItem("infinidoc_token");
                    router.push("/home");
                } else {
                    loginState.value.loggedIn = false;
                    // remove token
                    localStorage.removeItem("infinidoc_token");
                    router.push("/login");
                }
            }
        );
    } else {
        router.push("/");
    }
});
</script>
