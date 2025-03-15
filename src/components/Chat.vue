<template>
    <div class="home-main">
        <div class="main-left">
            <ChatSelect></ChatSelect>
        </div>
        <div class="main-main">
            <HeadBar>InfiniDoc 写作</HeadBar>
        </div>
    </div>
</template>
<script setup>
import ChatSelect from "./ChatSelect.vue";
import HeadBar from "./headBar.vue";

import { inject, provide } from "vue";
const loginState = inject("loginState");

provide("selectProject", (project_id) => selectProject(project_id));

const selectProject = (project_id) => {
    // todo
};
</script>
