<template>
    <div class="sup-paragraph">
        <div class="paragraph" :class="{ 'paragraph-selected': selected }">
            <div class="paragraph-control">
                <el-button
                    type="primary"
                    @click="$emit('moveup')"
                    v-show="isNotFirst"
                    >↑</el-button
                ><br />
                <el-button
                    type="primary"
                    @click="$emit('movedown')"
                    v-show="isNotLast"
                    >↓</el-button
                ><br />
                <el-popconfirm
                    title="确定删除吗"
                    confirm-button-text="删除"
                    confirm-button-type="text"
                    cancel-button-text="取消"
                    cancel-button-type="primary"
                    @confirm="$emit('delete')"
                >
                    <template #reference
                        ><el-button type="danger">删除</el-button></template
                    ></el-popconfirm
                >
            </div>
            <div class="paragraph-main" @click="$emit('select')">
                <el-input
                    v-model="model.title"
                    placeholder="标题"
                    style="width: 100%"
                ></el-input>
                <el-input
                    v-model="model.content"
                    type="textarea"
                    placeholder="内容"
                    style="width: 100%"
                    :autosize="{ minRows: 4 }"
                ></el-input>
            </div>
        </div>
        <div class="paragraph-divider" @click="handleInsert">+</div>
    </div>
</template>
<script setup>
import { defineModel, defineProps, defineEmits, inject } from "vue";
const model = defineModel();
const props = defineProps({
    isNotFirst: Boolean,
    isNotLast: Boolean,
    selected: Boolean,
    index: Number,
});
const insertNewParagraphBefore = inject("insertNewParagraphBefore");

const handleInsert = () => {
    insertNewParagraphBefore(props.index + 1);
};
const emit = defineEmits(["select", "moveup", "movedown", "delete"]);
</script>
