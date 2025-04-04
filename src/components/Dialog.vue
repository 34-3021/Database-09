<template>
    <div class="dialog">
        <div class="dialog-control">
            <el-button
                type="primary"
                class="iconfont dialog-control-button"
                @click="useParagraph(content)"
                v-if="role == 'AI'"
                >&#xe66d;</el-button
            ><br v-if="role == 'AI'" />
            <el-button
                type="primary"
                class="iconfont dialog-control-button"
                text
                @click="folded = !folded"
                v-if="
                    content.length > 100 && (content.length <= 1000 || !folded)
                "
            >
                {{ folded ? "&#xe673;" : "&#xe666;" }}
            </el-button>
            <br
                v-if="
                    content.length > 100 && (content.length <= 1000 || !folded)
                "
            />
            <el-popconfirm
                :title="unfold_warning"
                confirm-button-text="展开"
                confirm-button-type="text"
                cancel-button-text="取消"
                cancel-button-type="primary"
                @confirm="folded = !folded"
                v-if="content.length > 1000 && folded"
            >
                <template #reference
                    ><el-button
                        type="danger"
                        text
                        class="iconfont dialog-control-button"
                        >{{ folded ? "&#xe673;" : "&#xe666;" }}</el-button
                    ></template
                ></el-popconfirm
            ><br v-if="content.length > 1000 && folded" />
            <el-popconfirm
                title="确定删除吗"
                confirm-button-text="删除"
                confirm-button-type="text"
                cancel-button-text="取消"
                cancel-button-type="primary"
                @confirm="deleteMessage(index)"
            >
                <template #reference
                    ><el-button
                        type="danger"
                        text
                        class="iconfont dialog-control-button"
                        >&#xe665;</el-button
                    ></template
                ></el-popconfirm
            >
        </div>
        <div class="dialog-right">
            <div class="dialog-role">
                {{ role }} <span class="chatdate">{{ formatDate(time) }}</span>
            </div>
            <div class="dialog-content" v-if="!folded">{{ content }}</div>
            <div class="dialog-content" v-if="folded">
                {{ content_substring }}<br />... 已折叠，共
                {{ content.length }}个字符
            </div>
        </div>
    </div>
</template>
<script setup>
/* props: role, content */
import { defineProps, inject, onMounted, ref, watch } from "vue";
const useParagraph = inject("useParagraph");
const deleteMessage = inject("deleteMessage");
const content_substring = ref("");
const unfold_warning = ref("");
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

const get_content_substring = (content) => {
    if (!content) {
        return content;
    }
    if (content.length <= 100) {
        return content;
    }
    // need to precisely cut words, not characters
    let initial_ = content.substring(0, 25);
    // check if content[24] is a letter or a number
    if (initial_[24].match(/[a-zA-Z0-9]/)) {
        //find next space character
        for (let i = 25; i < content.length; i++) {
            if (
                content[i] == " " ||
                content[i] == "\n" ||
                content[i] == "\r" ||
                content[i] == "\t"
            ) {
                initial_ = content.substring(0, i);
                break;
            }
        }
    }
    return initial_;
};

onMounted(() => {
    if (props.content.length > 100 && props.role != "AI") {
        folded.value = true;
    }
    content_substring.value = get_content_substring(props.content);
    unfold_warning.value =
        "确定展开吗？原文长度为 " + props.content.length + "个字符";
});

watch(
    () => props.content,
    (newValue) => {
        if (newValue.length > 100 && props.role != "AI") {
            folded.value = true;
        } else {
            folded.value = false;
        }
        content_substring.value = get_content_substring(newValue);
        unfold_warning.value =
            "确定展开吗？原文长度为 " + newValue.length + "个字符";
    }
);
</script>
