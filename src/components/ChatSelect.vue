<template>
    <div id="menu-title">对话</div>
    <div id="menu-selections">
        <div
            class="menu-selection"
            v-for="chat in chats"
            :key="chat.id"
            @click="selectChat(chat.id)"
        >
            {{ chat.name }}
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";

const chats = ref([
    {
        id: "aaaaa",
        name: "对话1",
    },
    {
        id: "bbbbb",
        name: "对话2",
    },
    {
        id: "ccccc",
        name: "对话3",
    },
]);
</script>
