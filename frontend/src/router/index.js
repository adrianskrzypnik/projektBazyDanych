import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AddAdView from '../views/AddAdView.vue'
import AdView from '../views/AdView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminPanelView from "@/views/AdminPanelView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/add_ad',
      name: 'add_ad',
      component: AddAdView,
    },
    {
      path: '/ad',
      name: 'ad',
      component: AdView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPanelView,
    }
  ],
})

export default router
