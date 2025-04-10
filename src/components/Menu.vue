<template>
    <div>
        <div id="menu-title">菜单</div>
        <div id="menu-selections">
            <div id="menu-selections-top">
                <div
                    class="menu-selection"
                    @click="switchPageProtected('Papers')"
                >
                    &#xe66f;论文库
                </div>
                <div
                    class="menu-selection"
                    @click="switchPageProtected('Chat')"
                >
                    &#xe670;写作
                </div>
                <div
                    class="menu-selection"
                    @click="switchPageProtected('Search')"
                >
                    &#xe67f;搜索
                </div>
                <div
                    class="menu-selection"
                    @click="switchPageProtected('Settings')"
                >
                    &#xe67e;设置
                </div>
            </div>
            <div id="menu-selections-bottom">
                <div class="menu-selection" @click="logout">
                    &#xe67d;退出登录
                </div>
            </div>
        </div>
        <el-dialog v-model="dialogVisible" title="注意" width="500">
            <span>当前项目未保存。下一步该干什么？</span>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button
                    ><el-button type="danger" @click="forceSelect">
                        不保存并切换功能
                    </el-button>
                    <el-button type="primary" @click="saveandSelect">
                        保存并切换功能
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>
<script setup>
import { useRouter } from "vue-router";
import { inject, ref, defineProps } from "vue";

const props = defineProps({
    curPage: String,
});

//provide("switchPage", (page) => switchPage(page));
const switchPage = inject("switchPage");
const loginState = inject("loginState");
const dialogVisible = ref(false);

const Projects = inject("Projects");

const router = useRouter();

const logout = () => {
    loginState.value.loggedIn = false;
    loginState.value.token = "";
    localStorage.removeItem("infinidoc_token");
    router.push("/");
};

const target_page = ref("");

const switchPageProtected = (page) => {
    if (page === props.curPage) {
        return;
    }
    if (
        Projects.value.ok_to_switch === undefined ||
        Projects.value.ok_to_switch()
    ) {
        switchPage(page);
    } else {
        dialogVisible.value = true;
        target_page.value = page;
    }
};

const forceSelect = () => {
    dialogVisible.value = false;
    switchPage(target_page.value);
};

const saveandSelect = () => {
    dialogVisible.value = false;
    Projects.value.saveProject();
    switchPage(target_page.value);
};
</script>
