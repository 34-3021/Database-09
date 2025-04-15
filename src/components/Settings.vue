<template>
    <div class="home-main">
        <div class="main-main">
            <HeadBar>InfiniDoc 设置</HeadBar>
            <div class="content">
                <h2>账户信息</h2>
                InfiniDoc Unique ID: {{ uniqueid }}<br />
                <h2>LLM 设置</h2>
                自定义大模型 Endpoint<br />
                <el-input
                    v-model="endpoint"
                    style="width: 240px"
                    placeholder="Please input"
                    @change="resetModels"
                /><br />
                自定义大模型 key<br />
                <el-input
                    v-model="key"
                    style="width: 240px"
                    placeholder="Please input"
                />
                <br />
                模型选择<br />
                <el-select
                    v-model="model"
                    placeholder="Select"
                    style="width: 240px"
                >
                    <el-option
                        v-for="item in models"
                        :key="item.id"
                        :label="item.id"
                        :value="item.id"
                    ></el-option> </el-select
                ><el-button type="primary" @click="updateModels"
                    >获取可用模型</el-button
                ><br />
                <el-button type="primary" @click="submitForm">保存</el-button
                ><br />
                测试对话
                <br />
                <el-input
                    v-model="userInput"
                    style="width: 240px"
                    placeholder="Please input"
                />
                <el-button type="primary" @click="sendMessage">发送</el-button>

                <div class="ai-response" ref="aiResponseContainer"></div>
            </div>
        </div>
    </div>
</template>
<script setup>
import HeadBar from "./headBar.vue";
import { inject, onMounted, ref } from "vue";
import { marked } from "marked";
import hljs from "highlight.js";
import { BACKEND_BASE_URL, WEBSOCKET_URL } from "./endpoints.js";

const loginState = inject("loginState");
const uniqueid = ref("");

const endpoint = ref("");
const key = ref("");
const model = ref("");

const aiResponseContainer = ref(null);

const userInput = ref("");
const aiResponse = ref("");

const models = ref([]);

const resetModels = () => {
    models.value = [];
};

const parseRender = (data) => {
    let container = aiResponseContainer.value;
    if (container) {
        container.innerHTML = marked.parse(data);
    }
    hljs.highlightAll();
};

const sendMessage = () => {
    //ws local.tmysam.top:8005
    aiResponse.value = "";
    let ws = new WebSocket(WEBSOCKET_URL + "/ws");
    ws.onopen = function () {
        ws.send(
            JSON.stringify({
                endpoint: endpoint.value,
                key: key.value,
                model: model.value,
                message: userInput.value,
                type: "test",
            })
        );
    };
    ws.onmessage = function (evt) {
        aiResponse.value += evt.data;
        parseRender(aiResponse.value);
    };
};

const getUniqueID = () => {
    return new Promise((resolve, reject) => {
        fetch(BACKEND_BASE_URL + "/settings/getUniqueID", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                token: loginState.value.token,
            }),
        })
            .then((res) => res.json())
            .then((res) => {
                resolve({
                    uniqueID: res.unique_id,
                });
            })
            .catch((error) => {
                reject(error);
            });
    });
};

const initSettings = async () => {
    setSettings({
        endpoint: "",
        key: "",
        model: "",
    });
};

const setSettings = async (settings) => {
    let res = await fetch(BACKEND_BASE_URL + "/user/settings/set", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            infiniDocToken: loginState.value.token,
        },
        body: JSON.stringify({
            data: settings,
        }),
    });
    res = await res.json();
    return res;
};

const getSettings = async () => {
    let res = await fetch(BACKEND_BASE_URL + "/user/settings", {
        headers: {
            infiniDocToken: loginState.value.token,
        },
    });
    res = await res.json();
    res = res.settings;
    //if not exits, init
    if (
        res.endpoint === undefined ||
        res.key === undefined ||
        res.model === undefined
    ) {
        await initSettings();
        return {
            endpoint: "",
            key: "KEY_NOT_NEEDED",
            model: "",
        };
    }

    return {
        endpoint: res.endpoint,
        key: res.key,
        model: res.model,
    };
};

const submitForm = async () => {
    if (key.value === "") {
        key.value = "KEY_NOT_NEEDED";
    }
    let res = await setSettings({
        endpoint: endpoint.value,
        key: key.value,
        model: model.value,
    });
    console.log(res);
    ElMessage({
        message: "保存成功",
        type: "success",
    });
};

const updateModels = async () => {
    getModels(endpoint.value, key.value).then((res) => {
        models.value = res;
    });
};

const getModels = async (endpoint, api_key) => {
    let res = await fetch(BACKEND_BASE_URL + "/llm/getModels", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            endpoint: endpoint,
            api_key: api_key,
        }),
    });
    res = await res.json();
    return res.data;
};

onMounted(() => {
    getUniqueID().then((res) => {
        uniqueid.value = res.uniqueID;
    });
    getSettings().then((res) => {
        endpoint.value = res.endpoint;
        key.value = res.key;
        model.value = res.model;
        updateModels();
    });
});
</script>
