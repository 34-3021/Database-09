<template>
    <div class="login-bg">
        <div class="login-box">
            <div class="login-box-title">登录</div>
            用户名<br /><el-input
                v-model="username"
                placeholder="用户名"
                class="full-width-input"
            ></el-input
            ><br />密码<br /><el-input
                v-model="password"
                placeholder="密码"
                class="full-width-input"
                type="password"
                show-password
            ></el-input
            ><br />
            <el-button
                type="primary"
                @click="handleLogin"
                class="full-width-button"
                >确认</el-button
            >

            <p class="form-suggestion">或</p>
            <el-button @click="goToRegister" class="full-width-button"
                >注册</el-button
            ><br />
            <el-button
                @click="loginWithTAuth"
                class="full-width-button"
                v-loading="tauthButtonBusy"
                >使用 TAuth 登录</el-button
            ><br />
            <el-button @click="" class="full-width-button" v-loading="false"
                >使用 GitHub 登录</el-button
            ><br />
            <el-button type="info" @click="goHome" class="full-width-button"
                >返回</el-button
            >
        </div>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";
import { ref, inject } from "vue";

import { loginTAuth, loginNative } from "./tauth";

const router = useRouter();
const goHome = () => {
    router.push("/");
};
const goToRegister = () => {
    router.push("/register");
};
const handleLogin = async () => {
    let res = await loginNative(username.value, password.value);
    if (res.status) {
        ElMessage({
            message: res.message,
            type: "success",
        });
        //router.push("/login");
        loginState.value.loggedIn = true;
        loginState.value.token = res.token;
        //memorize res.token
        localStorage.setItem("infinidoc_token", res.token);
        router.push("/home");
    } else {
        ElMessage({
            message: res.message,
            type: "error",
        });
    }
};
const tauthButtonBusy = ref(false);

const loginState = inject("loginState");

const loginWithTAuth = async () => {
    tauthButtonBusy.value = true;
    let res = await loginTAuth();
    if (res.status) {
        ElMessage({
            message: res.message,
            type: "success",
        });
        loginState.value.loggedIn = true;
        loginState.value.token = res.token;
        //memorize res.token
        localStorage.setItem("infinidoc_token", res.token);
        router.push("/home");
    } else {
        ElMessage({
            message: res.message,
            type: "error",
        });
    }
    tauthButtonBusy.value = false;
};

const username = ref("");
const password = ref("");
</script>
