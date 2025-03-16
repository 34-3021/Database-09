<template>
    <div class="home-main">
        <div class="main-left">
            <ChatSelect></ChatSelect>
        </div>
        <div class="main-main">
            <HeadBar>InfiniDoc 写作</HeadBar>
            <Project :project_id="project_id"></Project>
        </div>
    </div>
</template>
<script setup>
import ChatSelect from "./ChatSelect.vue";
import HeadBar from "./headBar.vue";
import Project from "./Project.vue";

import { inject, provide, ref } from "vue";
const loginState = inject("loginState");

const project_id = ref(0);

provide("selectProject", (project_id) => selectProject(project_id));

const selectProject = (_project_id) => {
    project_id.value = _project_id;
    // todo
};
</script>
