<template>
    <div class="project" v-loading="loading" @keyup.ctrl.s="saveProject">
        <div class="project-left">
            <div class="project-edit-status">
                项目名称<br />
                <el-input
                    v-model="projectData.project_name"
                    @change="renameProject"
                    placeholder="项目名称"
                    v-loading="new_name_loading"
                    class="project-name-input"
                ></el-input
                ><el-button
                    class="project-save-button"
                    type="primary"
                    @click="saveProject"
                    :loading="saving"
                    v-if="edited"
                    >保存</el-button
                ><el-popconfirm
                    title="确定还原吗"
                    confirm-button-text="还原"
                    confirm-button-type="text"
                    cancel-button-text="取消"
                    cancel-button-type="primary"
                    @confirm="loadProject()"
                    v-if="edited"
                    ><template #reference
                        ><el-button type="danger" class="iconfont"
                            >还原</el-button
                        ></template
                    ></el-popconfirm
                ><el-button
                    class="project-download-button"
                    type="primary"
                    @click="downloadDialogActive = true"
                    >导出</el-button
                >
            </div>
            <div class="project-edit-status" :class="{ 'edited-warn': edited }">
                {{ edited ? "*未保存" : "" }}
            </div>
            <div class="paragraphs">
                <div
                    class="paragraph-divider"
                    @click="insertNewParagraphBefore(0)"
                >
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
                <div
                    class="content cent3r"
                    v-if="
                        !projectData.paragraphs ||
                        projectData.paragraphs.length === 0
                    "
                >
                    【点击 + 以开始】
                </div>
            </div>
        </div>

        <div
            class="project-right"
            v-if="projectData.paragraphs && projectData.paragraphs.length > 0"
        >
            <div class="dialogs">
                <Dialog
                    v-for="(chat, index) in projectData.paragraphs[
                        selectedParagraph
                    ].chatHistory"
                    :role="chat.role"
                    :content="chat.content"
                    :time="chat.time"
                    :index="index"
                ></Dialog>
            </div>
            <div class="chat-input">
                <form
                    @submit.prevent="sendMessage"
                    class="input-form"
                    v-loading="userInputLoading"
                >
                    <el-input
                        placeholder="输入你的要求"
                        v-model="userInput"
                        class="user-input-prompt"
                    ></el-input>
                    <el-button type="primary" @click="sendMessage">
                        发送
                    </el-button>
                </form>
            </div>
        </div>
    </div>
    <el-dialog v-model="downloadDialogActive" title="导出选项" width="500">
        <el-form :model="form">
            <el-form-item label="格式" :label-width="formLabelWidth">
                <el-select
                    v-model="downloadOptions.format"
                    placeholder="选择导出格式"
                >
                    <el-option label="Markdown (.md)(本地)" value="md" />
                    <el-option label="Microsoft Word (.docx)" value="docx" />
                    <el-option label="PDF (.pdf)" value="pdf" />
                    <el-option label="HTML (.html)" value="html" />
                    <el-option label="LaTeX (.tex)" value="tex" />
                    <el-option label="ODT (.odt)" value="odt" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="downloadDialogActive = false"
                    >取消</el-button
                >
                <el-button type="primary" @click="handleExport()">
                    确认
                </el-button>
            </div>
        </template>
    </el-dialog>
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

const downloadDialogActive = ref(false);
const downloadOptions = ref({
    format: "md",
});
const loading = ref(false);
const new_name_loading = ref(false);

const userInput = ref("");
const userInputLoading = ref(false);

const edited = ref(false);

const downloadFile = (_blob, filename) => {
    const url = window.URL.createObjectURL(_blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
        a.remove();
    }, 100);
};

const exportMarkDown = () => {
    let paragraphs = projectData.value.paragraphs;
    let content = "# " + projectData.value.project_name + "\n\n";
    for (let i = 0; i < paragraphs.length; i++) {
        content += "## " + paragraphs[i].title + "\n\n";
        content += paragraphs[i].content + "\n\n";
    }
    content += "\n\n";
    return content;
};

const handleExport = async () => {
    const format = downloadOptions.value.format;
    const content = exportMarkDown();
    const valid_formats = ["docx", "pdf", "html", "tex", "odt"];
    if (format === "md") {
        const blob = new Blob([content], { type: "text/markdown" });
        downloadFile(blob, projectData.value.project_name + ".md");
    } else if (valid_formats.includes(format)) {
        const response = await fetch(`https://local.tmysam.top:8001/convert`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                markdown: content,
                target: format,
            }),
        });
        const blob = await response.blob();
        downloadFile(blob, projectData.value.project_name + "." + format);
    } else {
        console.error("Invalid format:", format);
    }
    downloadDialogActive.value = false;
};

const sendMessage = async () => {
    //userInputLoading.value = true;
    if (userInput.value.trim() === "") return;
    projectData.value.paragraphs[selectedParagraph.value].chatHistory.push({
        role: "User",
        content: userInput.value,
        time: Date.now(),
    });
    let ws = new WebSocket("wss://local.tmysam.top:8001/ws");
    ws.onopen = function () {
        ws.send(
            JSON.stringify({
                project_name: projectData.value.project_name,
                paragraph_title:
                    projectData.value.paragraphs[selectedParagraph.value].title,
                paragraph_current_content:
                    projectData.value.paragraphs[selectedParagraph.value]
                        .content,
                user_prompt: userInput.value,
                token: loginState.value.token,
                type: "project",
            })
        );
    };
    ws.onmessage = function (evt) {
        if (evt.data == "--DDONE--") {
            ws.close();
            return;
        }
        if (evt.data == "--DONE--") {
            return;
        }
        if (evt.data == "--AI PROG--") {
            projectData.value.paragraphs[
                selectedParagraph.value
            ].chatHistory.push({
                role: "AI In Progress",
                content: "",
                time: Date.now(),
            });
            return;
        }
        if (evt.data == "--AI--") {
            projectData.value.paragraphs[
                selectedParagraph.value
            ].chatHistory.push({
                role: "AI",
                content: "",
                time: Date.now(),
            });
            return;
        }
        if (evt.data == "--SYSTEM--") {
            projectData.value.paragraphs[
                selectedParagraph.value
            ].chatHistory.push({
                role: "System",
                content: "",
                time: Date.now(),
            });
            return;
        }

        projectData.value.paragraphs[selectedParagraph.value].chatHistory[
            projectData.value.paragraphs[selectedParagraph.value].chatHistory
                .length - 1
        ].content += evt.data;
    };
};

const deleteMessage = (index) => {
    projectData.value.paragraphs[selectedParagraph.value].chatHistory.splice(
        index,
        1
    );
};

provide("deleteMessage", (index) => deleteMessage(index));

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

const saving = ref(false);

const saveProject = async () => {
    if (saving.value) return;
    saving.value = true;
    let notification_instance = ElNotification({
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
    notification_instance.close();
    edited.value = false;
    saving.value = false;
};

const keydownHandler = (e) => {
    if (e.repeat) return;
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

const useParagraph = (content) => {
    projectData.value.paragraphs[selectedParagraph.value].content = content;
};

provide("useParagraph", (content) => useParagraph(content));

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
