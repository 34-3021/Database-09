<template>
    <div class="dialog">
        <div class="dialog-role">
            {{ role }} <span class="chatdate">{{ formatDate(time) }}</span>
        </div>
        <div class="dialog-content">{{ content }}</div>
        <el-button
            type="primary"
            @click="useParagraph(content)"
            v-if="role == 'AI'"
            >使用</el-button
        >
    </div>
</template>
<script setup>
/* props: role, content */
import { defineProps, inject } from "vue";
const useParagraph = inject("useParagraph");

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
});
</script>
