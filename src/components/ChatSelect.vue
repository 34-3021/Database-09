<template>
    <div id="menu-title">项目</div>
    <div id="menu-selections" v-loading="loading">
        <div
            class="menu-selection"
            v-for="pj in projects"
            :key="pj.project_id"
            @click="selectProject(pj.project_id)"
        >
            <span class="project-name">{{ pj.project_name }}</span>
            <el-popconfirm
                title="确定删除吗"
                confirm-button-text="删除"
                confirm-button-type="text"
                cancel-button-text="取消"
                cancel-button-type="primary"
                @confirm="deleteProject(pj.project_id)"
            >
                <template #reference>
                    <el-button type="danger" class="iconfont" circle
                        >&#xe665;</el-button
                    ></template
                >
            </el-popconfirm>
        </div>
        <el-button
            type="primary"
            @click="newProject('Untitled')"
            class="new-project-button"
            v-loading="newProjectLoading"
            >新建项目</el-button
        >
    </div>
</template>

<script setup>
import { inject, onMounted, ref, watch } from "vue";

const loginState = inject("loginState");

const selectProject = inject("selectProject");

const newProjectLoading = ref(false);

const loading = ref(false);

const getProjects = async () => {
    loading.value = true;
    try {
        let res = await fetch("https://local.tmysam.top:8001/project/get", {
            headers: {
                infiniDocToken: loginState.value.token,
            },
        });
        let data = await res.json();
        projects.value = data.projects;
    } finally {
        loading.value = false;
    }
};

defineExpose({
    getProjects,
});

const deleteProject = async (project_id) => {
    let res = await fetch("https://local.tmysam.top:8001/project/delete", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            infiniDocToken: loginState.value.token,
        },
        body: JSON.stringify({
            project_id: project_id,
        }),
    });
    let data = await res.json();
    getProjects();
};

const newProject = async (name) => {
    newProjectLoading.value = true;
    try {
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
    } finally {
        newProjectLoading.value = false;
    }

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

onMounted(() => {
    getProjects();
});
</script>
