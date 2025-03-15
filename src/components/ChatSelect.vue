<template>
    <div id="menu-title">项目</div>
    <div id="menu-selections">
        <div
            class="menu-selection"
            v-for="pj in projects"
            :key="pj.project_id"
            @click="selectProject(pj.project_id)"
        >
            {{ pj.project_name }}
        </div>
        <el-button type="primary" @click="newProject('Untitled')"
            >新建项目</el-button
        >
    </div>
</template>

<script setup>
import { inject, onMounted, ref, watch } from "vue";

const loginState = inject("loginState");

const selectProject = inject("selectProject");

const getProjects = async () => {
    let res = await fetch("https://local.tmysam.top:8001/project/get", {
        headers: {
            infiniDocToken: loginState.value.token,
        },
    });
    let data = await res.json();
    projects.value = data.projects;
};

const newProject = async (name) => {
    let res = await fetch("https://local.tmysam.top:8001/project/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            infiniDocToken: loginState.value.token,
        },

        body: JSON.stringify({
            project_name: name,
        }),
    });
    let data = await res.json();
    getProjects();
};
const projects = ref([]);

// watch loginState.token

watch(
    () => loginState.value.token,
    (newVal) => {
        getProjects();
    }
);

onMounted(() => {});
</script>
