<template>
    <div class="home-main">
        <div class="main-main">
            <HeadBar>论文库</HeadBar>
            <div class="content">
                <div class="uploader">
                    <el-upload
                        ref="uploadRef"
                        class="upload-demo"
                        action="https://local.tmysam.top:8001/upload"
                        :headers="headers"
                        :multiple="true"
                        :auto-upload="false"
                        :on-success="refreshDefault"
                        ><template #trigger>
                            <el-button type="primary">选择文件以上传</el-button>
                        </template>
                        <el-button
                            class="ml-3"
                            type="success"
                            @click="submitUpload"
                        >
                            全部上传
                        </el-button>
                    </el-upload>
                </div>
                <div>
                    <el-input
                        placeholder="请输入搜索内容"
                        class="search-input"
                        suffix-icon="el-icon-search"
                        size="small"
                        clearable
                        v-model="searchKey"
                    ></el-input>
                    <el-button type="primary" size="small" @click="search"
                        >搜索</el-button
                    >
                </div>
                <el-table :data="tableData" stripe style="width: 100%">
                    <el-table-column prop="name" label="文件名" width="180" />
                    <el-table-column prop="size" label="大小" width="180">
                        <template #default="scope">{{
                            friendlySize(scope.row.size)
                        }}</template>
                    </el-table-column>
                    <el-table-column prop="operation" label="操作">
                        <template #default="scope">
                            <el-button
                                type="primary"
                                size="mini"
                                @click="downloadFile(scope.row.seq)"
                            >
                                下载
                            </el-button>
                            <el-button
                                type="danger"
                                size="mini"
                                @click="deleteFile(scope.row.seq)"
                                :disabled="scope.row.deleting !== undefined"
                            >
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <el-pagination
                    background
                    layout="prev, pager, next"
                    :page-count="totalPages"
                    v-model:current-page="curPage"
                />
            </div>
        </div>
    </div>
</template>
<script setup>
import { ta } from "element-plus/es/locales.mjs";
import HeadBar from "./headBar.vue";
import { inject, onMounted, ref, watch } from "vue";

const loginState = inject("loginState");

const headers = ref({
    infiniDocToken: loginState.value.token,
});

const uploadRef = ref();

const totalPages = ref(1);

const curPage = ref(1);

const searchKey = ref("");
const search = async () => {
    if (searchKey.value === "") {
        return;
    }
    let key = encodeURIComponent(searchKey.value);
    let res = await fetch(
        `https://local.tmysam.top:8001/search?keyword=${key}`,
        {
            method: "GET",
            headers: {
                infiniDocToken: loginState.value.token,
            },
        }
    );
    let data = await res.json();
    console.log(data);
};
const submitUpload = () => {
    uploadRef.value.submit();
};

watch(
    () => loginState.value.token,
    (newVal) => {
        headers.value.infiniDocToken = newVal;
    }
);

watch(
    () => curPage.value,
    (newVal) => {
        fetchPage(newVal);
    }
);

const friendlySize = (bytes) => {
    if (bytes < 1024) return bytes + "B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + "KB";
    if (bytes < 1024 * 1024 * 1024)
        return (bytes / 1024 / 1024).toFixed(2) + "MB";
    return (bytes / 1024 / 1024 / 1024).toFixed(2) + "GB";
};

const refreshDefault = () => {
    fetchPage(1);
    curPage.value = 1;
};

const fetchPage = async (pageNo) => {
    // https://local.tmysam.top:8001/fileList?limit=10&offset=10*(pageNo-1)
    // headers: {infiniDocToken: token}
    let offset = (pageNo - 1) * 10;
    let res = await fetch(
        `https://local.tmysam.top:8001/fileList?limit=10&offset=${offset}`,
        {
            method: "GET",
            headers: {
                infiniDocToken: loginState.value.token,
            },
        }
    );
    let data = await res.json();
    tableData.value = data.files;
    totalPages.value = Math.max(1, Math.floor(data.totalfiles / 10));
};

const downloadFile = async (seq) => {
    // https://local.tmysam.top:8001/download?seq=seq
    // headers: {infiniDocToken: token}
    let res = await fetch(`https://local.tmysam.top:8001/download?seq=${seq}`, {
        method: "GET",
        headers: {
            infiniDocToken: loginState.value.token,
        },
    });
    let blob = await res.blob();
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    console.log(res.headers.get("Fname"));
    a.download = res.headers.get("Content-Disposition").split("=")[1];
    a.click();
    window.URL.revokeObjectURL(url);
};

const deleteFile = async (seq) => {
    tableData.value.find((item) => item.seq === seq).deleting = true;
    // https://local.tmysam.top:8001/delete?seq=seq
    // headers: {infiniDocToken: token}
    let res = await fetch(`https://local.tmysam.top:8001/delete?seq=${seq}`, {
        method: "GET",
        headers: {
            infiniDocToken: loginState.value.token,
        },
    });
    let data = await res.json();
    if (data.success) {
        fetchPage(1);
        tableData.value.find((item) => item.seq === seq).deleting = undefined;
    }
};

const tableData = ref([]);

onMounted(() => {
    fetchPage(1);
});
</script>
