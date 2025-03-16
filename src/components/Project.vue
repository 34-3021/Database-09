<template>
    <div class="project">
        <div class="paragraphs">
            <Paragraph
                v-for="(paragraph, index) in projectData.paragraphs"
                v-model="projectData.paragraphs[index]"
                @click="selectedParagraph = index"
                :class="{ 'paragraph-selected': selectedParagraph === index }"
            ></Paragraph>
        </div>
        <div class="chatbox">
            <Dialog
                v-for="chat in projectData.paragraphs[selectedParagraph]
                    .chatHistory"
                :role="chat.role"
                :content="chat.content"
            ></Dialog>
        </div>
    </div>
</template>
<script setup>
import { defineProps, ref } from "vue";
import Dialog from "./Dialog.vue";
import Paragraph from "./Paragraph.vue";

const selectedParagraph = ref(0);

const projectData = ref({
    project_id: 0,
    paragraphs: [
        {
            title: "paragraph1",
            content: "content1",
            chatHistory: [
                {
                    role: "User",
                    content: "xxxx",
                },
                {
                    role: "Bot",
                    content: "xxxx",
                },
            ],
        },
        {
            title: "paragraph2",
            content: "content2",
            chatHistory: [
                {
                    role: "User",
                    content: "yyyy",
                },
                {
                    role: "Bot",
                    content: "yyyy",
                },
            ],
        },
    ],
});
// a prop to receive the project_id
const props = defineProps({
    project_id: Number,
});
</script>
