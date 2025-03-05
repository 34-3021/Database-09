<template>
    <div class="login-bg">
        <div class="login-box">
            <div class="login-box-title">注册</div>
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
            ></el-input
            ><br />确认密码<br /><el-input
                v-model="password"
                placeholder="确认密码"
                class="full-width-input"
                type="password"
            ></el-input
            ><br />

            <el-button
                type="primary"
                @click="handleRegister"
                class="full-width-button"
                >确认</el-button
            ><br />
            <el-button @click="goToLogin" class="full-width-button"
                >登录</el-button
            ><br />
            <el-button type="info" @click="goHome" class="full-width-button"
                >返回</el-button
            >
        </div>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";

const router = useRouter();
const goHome = () => {
    router.push("/");
};
const goToLogin = () => {
    router.push("/login");
};
const handleRegister = () => {
    //todo
    router.push("/home");
};

const username = ref("");
const password = ref("");
</script>
