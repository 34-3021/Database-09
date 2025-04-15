<template>
    <div class="home-main">
        <div class="main-main">
            <HeadBar>搜索</HeadBar>
            <div class="content">
                <div v-loading="loading">
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
                    <div class="search-result-cards">
                        <SearchResultCard
                            v-for="item in searchResults"
                            :resultObj="item"
                        ></SearchResultCard>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import HeadBar from "./headBar.vue";
import SearchResultCard from "./SearchResultCard.vue";
import { inject, onMounted, ref, watch } from "vue";
import { BACKEND_BASE_URL, WEBSOCKET_URL } from "./endpoints";

const loginState = inject("loginState");
const headers = ref({
    infiniDocToken: loginState.value.token,
});

const searchResults = ref([]);
const searchKey = ref("");
const loading = ref(false);
const search = async () => {
    if (searchKey.value === "") {
        return;
    }
    loading.value = true;
    let key = encodeURIComponent(searchKey.value);
    let res = await fetch(BACKEND_BASE_URL + `/search?keyword=${key}`, {
        method: "GET",
        headers: {
            infiniDocToken: loginState.value.token,
        },
    });
    let data = await res.json();
    // data.result alike "filename":{"chunkx":"content","chunky":"content"}
    // convert to array [{"filename":"filename","chunks":{"chunkx":"content","chunky":"content"}}
    //]
    let result = Object.keys(data.result).map((filename) => {
        return {
            filename: filename,
            chunks: data.result[filename],
        };
    });
    searchResults.value = result;
    loading.value = false;
};

watch(
    () => loginState.value.token,
    (newVal) => {
        headers.value.infiniDocToken = newVal;
    }
);
</script>
