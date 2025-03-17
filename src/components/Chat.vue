<template>
    <div class="home-main">
        <div class="main-left">
            <ChatSelect ref="selector"></ChatSelect>
        </div>
        <div class="main-main">
            <HeadBar>InfiniDoc 写作</HeadBar>
            <Project
                :project_id="project_id"
                v-if="project_id != -1"
                ref="pj"
            ></Project>
        </div>
        <el-dialog v-model="dialogVisible" title="注意" width="500">
            <span>当前项目未保存。下一步该干什么？</span>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button
                    ><el-button type="danger" @click="forceSelectProject">
                        不保存并切换项目
                    </el-button>
                    <el-button type="primary" @click="saveandSelectProject">
                        保存并切换项目
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>
<script setup>
import ChatSelect from "./ChatSelect.vue";
import HeadBar from "./headBar.vue";
import Project from "./Project.vue";

import { inject, provide, ref } from "vue";
const loginState = inject("loginState");

const dialogVisible = ref(false);
const project_id = ref(-1);

const target_project_id = ref(-1);

const selector = ref(null);

const pj = ref(null);

provide("selectProject", (project_id) => selectProject(project_id));

const reloadProjects = async () => {
    await selector.value.getProjects();
};

provide("reloadProjects", reloadProjects);

const forceSelectProject = () => {
    project_id.value = target_project_id.value;
    dialogVisible.value = false;
};

const saveandSelectProject = () => {
    pj.value.saveProject();
    project_id.value = target_project_id.value;
    dialogVisible.value = false;
};

const selectProject = (_project_id) => {
    if (_project_id === project_id.value) return;
    if (!pj.value || !pj.value.edited) {
        project_id.value = _project_id;
        return;
    }
    dialogVisible.value = true;
    target_project_id.value = _project_id;
};
</script>
