<template>
    <div class="dialog">
        <div class="dialog-role">{{ role }}</div>
        <div class="dialog-content">{{ content }}</div>
    </div>
</template>
<script setup>
/* props: role, content */
import { defineProps } from "vue";
const props = defineProps({
    role: String,
    content: String,
});
</script>
