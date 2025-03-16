<template>
    <div class="paragraph">
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
        ></el-input>
    </div>
</template>
<script setup>
import { defineModel } from "vue";
const model = defineModel();
</script>
