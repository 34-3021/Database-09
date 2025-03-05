<template>
    <div>
        <div id="menu-title">菜单</div>
        <div id="menu-selections">
            <div class="menu-selection" @click="">论文库</div>
            <div class="menu-selection" @click="switchPage('Chat')">对话</div>

            <div class="menu-selection" @click="switchPage('Settings')">
                设置
            </div>
            <div class="menu-selection" @click="logout">退出登录</div>
        </div>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";
import { inject } from "vue";

const logout = () => {
    router.push("/");
};
//provide("switchPage", (page) => switchPage(page));
const switchPage = inject("switchPage");

const router = useRouter();
</script>
