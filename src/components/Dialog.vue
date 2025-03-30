<template>
    <div class="dialog">
        <div class="dialog-role">
            {{ role }} <span class="chatdate">{{ formatDate(time) }}</span>
        </div>
        <div class="dialog-content" v-if="!folded">{{ content }}</div>
        <el-button
            type="primary"
            @click="useParagraph(content)"
            v-if="role == 'AI'"
            >使用</el-button
        >
        <el-button
            type="primary"
            @click="folded = !folded"
            v-if="content.length > 100"
        >
            {{ folded ? "展开" : "收起" }}
        </el-button>
        <el-button type="danger" @click="deleteMessage(index)">删除</el-button>
    </div>
</template>
<script setup>
/* props: role, content */
import { defineProps, inject, onMounted, ref, watch } from "vue";
const useParagraph = inject("useParagraph");
const deleteMessage = inject("deleteMessage");
const folded = ref(false);

const formatDate = (date) => {
    var d = new Date(date),
        month = "" + (d.getMonth() + 1),
        day = "" + d.getDate(),
        year = d.getFullYear(),
        hour = d.getHours(),
        minute = d.getMinutes(),
        second = d.getSeconds();

    if (month.length < 2) month = "0" + month;
    if (day.length < 2) day = "0" + day;
    if (hour.length < 2) hour = "0" + hour;
    if (minute.length < 2) minute = "0" + minute;
    if (second.length < 2) second = "0" + second;

    return (
        [year, month, day].join("-") + " " + [hour, minute, second].join(":")
    );
};

const props = defineProps({
    role: String,
    time: Number,
    content: String,
    index: Number,
});

onMounted(() => {
    if (props.content.length > 100 && props.role != "AI") {
        folded.value = true;
    }
});

watch(
    () => props.content,
    (newValue) => {
        if (newValue.length > 100 && props.role != "AI") {
            folded.value = true;
        } else {
            folded.value = false;
        }
    }
);
</script>
