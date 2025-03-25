<template>
    <div id="not-logged-in-view">
        <NotLoggedInMenu id="menu"></NotLoggedInMenu>
        <div id="main">
            <HeadBar>InfiniDoc</HeadBar>
            <div id="main-desc">
                <div class="feature">
                    <div class="feature-title">
                        与任意 API 结合使用<span class="sup">[1]</span>
                    </div>
                    <div class="feature-description">
                        您可以选择您喜欢的大语言模型接入本系统，以提供定制化和个性化的服务。
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-title">多端同步的使用体验</div>
                    <div class="feature-description">
                        您的信息将被安全地存放在云端<span class="sup">[2]</span
                        >，供您在任何位置和设备随时使用。
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-title">论文导入方式</div>
                    <div class="feature-description">
                        支持 PDF 导入<span class="sup">[3]</span>。
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-title">自动的引用联想</div>
                    <div class="feature-description">
                        当您提出要求时，如果相关文本涉及引用到的文献，且该文献已加入论文库，大模型将考虑被引用文献的内容。
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-title">流式生成</div>
                    <div class="feature-description">
                        将实时生成的文本流式传输到您的设备。
                    </div>
                </div>
            </div>

            <div id="footnotes-outer">
                <div class="footnotes-content">
                    <div>
                        [1] 任意 API 指使用 OpenAI 类似模式的，兼容 OpenAI API
                        调用方法的用户提供的第三方接口。当使用第三方接口时，不对内容的准确性和服务可用性做出任何保证。用户应当保证其提供的接口符合用户当地以及服务提供地（中国大陆）的相关法律法规。在使用用户提供的
                        API
                        时，由于上下文长度等限制，可能无法保证所有服务的正常运行。
                    </div>
                    <div>
                        [2]
                        聊天记录等信息将经过加密，您的论文原始文件将由第三方提供的存储方案解决。我们保证信息不会在我们管理的范围内泄露。关于更详细信息，请参考我们的隐私政策。
                    </div>
                    <div>
                        [3]
                        由于您上传文本的版权问题导致的任何法律问题，我们不承担任何责任。arXiv
                        运营由康奈尔大学的 arXiv 领导团队和 arXiv
                        员工负责。arXiv 的管理由领导团队领导，并受到 arXiv
                        编辑顾问委员会、机构顾问委员会和科学顾问委员会的指导。arXiv
                        是一个社区支持的资源，由康奈尔大学、西蒙斯基金会、成员机构和捐助者资助。
                    </div>
                </div>
            </div>
            <div id="bottom">
                <div class="main-copy">
                    Copyright &copy; 2025 TSStudio InfiniWare. All rights
                    reserved.
                    <RouterLink to="/privacy-policy" class="privacy-policy-link"
                        >Privacy Policy
                    </RouterLink>
                </div>
                <div class="main-copy">
                    版权所有 &copy; 2025 TSStudio InfiniWare。保留所有权利。
                    <RouterLink to="/privacy-policy" class="privacy-policy-link"
                        >隐私政策
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { RouterLink } from "vue-router";
import NotLoggedInMenu from "./NotLoggedInMenu.vue";
import HeadBar from "./headBar.vue";
import { onMounted, ref, inject, provide } from "vue";

const menuOn = ref(false);
const toggleMenu = () => {
    if (menuOn.value) {
        document.getElementById("menu").style.marginLeft =
            "-" + document.getElementById("menu").offsetWidth + "px";
        menuOn.value = false;
    } else {
        document.getElementById("menu").style.marginLeft = "0";
        menuOn.value = true;
    }
};
provide("toggleMenu", toggleMenu);

const toggleDarkModeParent = inject("toggleDarkMode");

const toggleDarkMode = () => {
    toggleDarkModeParent();
};

onMounted(() => {
    document.getElementById("menu").style.marginLeft =
        "-" + document.getElementById("menu").offsetWidth + "px";
});
</script>
