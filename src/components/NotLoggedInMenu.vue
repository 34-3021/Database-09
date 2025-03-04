<template>
    <div>
        <div id="menu-title">菜单</div>
        <div id="menu-selections">
            <div class="menu-selection" @click="goToLogin">登录</div>
            <div class="menu-selection" @click="goToRegister">注册</div>
        </div>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const goToLogin = () => {
    router.push("/login");
};
const goToRegister = () => {
    router.push("/register");
};
</script>
