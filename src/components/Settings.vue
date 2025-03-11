<template>
    <div class="home-main">
        <div class="main-main">
            <HeadBar>InfiniDoc 设置</HeadBar>
            <div class="content">Unique ID:{{ uniqueid }}</div>
        </div>
    </div>
</template>
<script setup>
import ChatSelect from "./ChatSelect.vue";
import HeadBar from "./headBar.vue";
import { inject, onMounted, ref } from "vue";

const loginState = inject("loginState");
const uniqueid = ref("");

const getUniqueID = () => {
    return new Promise((resolve, reject) => {
        fetch("https://local.tmysam.top:8001/settings/getUniqueID", {
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

onMounted(() => {
    getUniqueID().then((res) => {
        uniqueid.value = res.uniqueID;
    });
});
</script>
