import { createWebHashHistory, createRouter } from "vue-router";

import HomeView from "./components/HomeView.vue";
import NotLoggedInView from "./components/NotLoggedInView.vue";
import RegisterView from "./components/RegisterView.vue";
import LoginView from "./components/LoginView.vue";
import PrivacyPolicy from "./components/PrivacyPolicy.vue";

const routes = [
    { path: "/", component: NotLoggedInView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/privacy-policy", component: PrivacyPolicy },
    { path: "/home", component: HomeView },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

export default router;
