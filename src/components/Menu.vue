<template>
    <div>
        <div id="menu-title">菜单</div>
        <div id="menu-selections">
            <div class="menu-selection" @click="">论文库</div>
            <div class="menu-selection" @click="">对话</div>
            <div class="menu-selection" @click="">退出登录</div>
        </div>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>
