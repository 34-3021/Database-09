<template>
    <div class="project" v-loading="loading" @keyup.ctrl.s="saveProject">
        <div class="project-edit-status">
            <el-input
                v-model="projectData.project_name"
                @change="renameProject"
                placeholder="项目名称"
                v-loading="new_name_loading"
                class="project-name-input"
            ></el-input>
            {{ edited ? "*未保存" : "" }}
        </div>
        <div class="paragraphs">
            <div class="paragraph-divider" @click="insertNewParagraphBefore(0)">
                +
            </div>
            <Paragraph
                v-for="(paragraph, index) in projectData.paragraphs"
                v-model="projectData.paragraphs[index]"
                @select="selectedParagraph = index"
                :selected="selectedParagraph === index"
                :isNotFirst="index !== 0"
                :isNotLast="index !== projectData.paragraphs.length - 1"
                :index="index"
                @moveup="moveup(index)"
                @movedown="movedown(index)"
                @delete="deleteParagraph(index)"
            ></Paragraph>
        </div>
        <div
            class="chatbox"
            v-if="projectData.paragraphs && projectData.paragraphs.length > 0"
        >
            <Dialog
                v-for="chat in projectData.paragraphs[selectedParagraph]
                    .chatHistory"
                :role="chat.role"
                :content="chat.content"
            ></Dialog>
        </div>
    </div>
</template>
<script setup>
import {
    defineProps,
    ref,
    provide,
    inject,
    onMounted,
    onUnmounted,
    watch,
} from "vue";
import Dialog from "./Dialog.vue";
import Paragraph from "./Paragraph.vue";

const selectedParagraph = ref(0);
const loginState = inject("loginState");

const loading = ref(false);
const new_name_loading = ref(false);

const edited = ref(false);

const moveup = (index) => {
    if (index === 0) return;
    const temp = projectData.value.paragraphs[index];
    projectData.value.paragraphs[index] =
        projectData.value.paragraphs[index - 1];
    projectData.value.paragraphs[index - 1] = temp;
    selectedParagraph.value = index - 1;
};

const movedown = (index) => {
    if (index === projectData.value.paragraphs.length - 1) return;
    const temp = projectData.value.paragraphs[index];
    projectData.value.paragraphs[index] =
        projectData.value.paragraphs[index + 1];
    projectData.value.paragraphs[index + 1] = temp;
    selectedParagraph.value = index + 1;
};

const deleteParagraph = (index) => {
    projectData.value.paragraphs.splice(index, 1);
    if (selectedParagraph.value >= projectData.value.paragraphs.length) {
        selectedParagraph.value = projectData.value.paragraphs.length - 1;
    }
};

const insertNewParagraphBefore = (index) => {
    console.log("insertNewParagraphBefore", index);
    projectData.value.paragraphs.splice(index, 0, {
        title: "",
        content: "",
        chatHistory: [],
    });
};

provide("insertNewParagraphBefore", (index) => insertNewParagraphBefore(index));

const projectData = ref({
    project_id: 0,
    project_name: "",
    paragraphs: [],
});

// const projectData = ref({
//     project_id: 0,
//     project_name: "project_name",
//     paragraphs: [
//         {
//             title: "paragraph1",
//             content: "content1",
//             chatHistory: [
//                 {
//                     role: "User",
//                     content: "xxxx",
//                 },
//                 {
//                     role: "Bot",
//                     content: "xxxx",
//                 },
//             ],
//         },
//         {
//             title: "paragraph2",
//             content: "content2",
//             chatHistory: [
//                 {
//                     role: "User",
//                     content: "yyyy",
//                 },
//                 {
//                     role: "Bot",
//                     content: "yyyy",
//                 },
//             ],
//         },
//     ],
// });
// a prop to receive the project_id
const props = defineProps({
    project_id: Number,
});

const reloadProjects = inject("reloadProjects");
const renameProject = async () => {
    new_name_loading.value = true;
    try {
        const response = await fetch(
            `https://local.tmysam.top:8001/project/rename/${props.project_id}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    infiniDocToken: loginState.value.token,
                },
                body: JSON.stringify({
                    new_name: projectData.value.project_name,
                }),
            }
        );
        await reloadProjects();
    } finally {
        new_name_loading.value = false;
    }
};

const loadProject = async () => {
    loading.value = true;
    try {
        const response = await fetch(
            `https://local.tmysam.top:8001/project/getparagraphs/${props.project_id}`,
            {
                headers: {
                    infiniDocToken: loginState.value.token,
                },
            }
        );
        const data = await response.json();
        projectData.value.paragraphs = JSON.parse(data.paragraphs);

        const response2 = await fetch(
            `https://local.tmysam.top:8001/project/name/${props.project_id}`,
            {
                headers: {
                    infiniDocToken: loginState.value.token,
                },
            }
        );
        const data2 = await response2.json();
        projectData.value.project_name = data2.project_name;
    } finally {
        loading.value = false;
        edited.value = false;
    }
};

const saveProject = async () => {
    ElNotification({
        title: "保存中",
        message: "正在保存项目",
        type: "info",
    });
    const response = await fetch(
        `https://local.tmysam.top:8001/project/save/${props.project_id}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                infiniDocToken: loginState.value.token,
            },
            body: JSON.stringify({
                paragraphs: JSON.stringify(projectData.value.paragraphs),
            }),
        }
    );
    const data = await response.json();
    if (data.success) {
        ElNotification({
            title: "保存成功",
            message: "项目保存成功",
            type: "success",
        });
    } else {
        ElNotification({
            title: "保存失败",
            message: "项目保存失败",
            type: "error",
        });
    }
    edited.value = false;
};

const keydownHandler = (e) => {
    if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        saveProject();
    }
};

const unloadHandler = (e) => {
    if (edited.value) {
        e.preventDefault();
    }
};

onMounted(() => {
    loadProject();
    document.addEventListener("keydown", keydownHandler);
    window.addEventListener("beforeunload", unloadHandler);
});

onUnmounted(() => {
    document.removeEventListener("keydown", keydownHandler);
    window.removeEventListener("beforeunload", unloadHandler);
});

watch(
    () => props.project_id,
    (newVal) => {
        projectData.value.project_id = newVal;
        loadProject();
    }
);

defineExpose({ edited, saveProject });

watch(
    () => projectData.value.paragraphs,
    (newVal) => {
        edited.value = true;
    },
    { deep: true }
);
</script>
