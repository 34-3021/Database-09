<template>
    <div class="search-result-card">
        <div class="search-result-card-title">
            在 {{ resultObj.filename }} 提到
        </div>
        <div
            class="search-result-card-content"
            v-for="(value, key) in resultObj.chunks"
        >
            <div class="search-result-card-content-chunk">
                <div class="search-result-card-content-chunk-title">
                    {{ key }}
                </div>
                <div class="search-result-card-content-chunk-text">
                    {{ value }}
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { defineProps } from "vue";

const props = defineProps({
    resultObj: {
        type: Object,
        required: true,
    },
});
</script>
