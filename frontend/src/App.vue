<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-md">
      <div class="container mx-auto flex items-center justify-between p-4">
        <!-- Logo -->
        <div class="text-xl font-bold text-blue-600">
          <router-link to="/">
            Portal OLY
          </router-link>
        </div>
        <!-- Buttons -->
        <template v-if="userStore.user.isAuthenticated">

          <router-link to="/add_ad" class="text-gray-600 hover:text-red-600 transition duration-300 ease-in-out font-medium">
            Dodaj ogłoszenie
          </router-link>

          <router-link to="/profile" class="text-gray-600 hover:text-red-600 transition duration-300 ease-in-out font-medium">
            Mój Profil
          </router-link>

          <button @click="logout" class="text-gray-600 hover:text-red-600 transition duration-300 ease-in-out font-medium">
            Wyloguj się
          </button>
        </template>

        <template v-else>
          <div class="space-x-4">
            <router-link to="/login"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              Zaloguj
            </router-link>
            <router-link to="/register"
              class="px-4 py-2 text-sm font-medium text-blue-600 border border-blue-600 rounded hover:bg-blue-100"
            >
              Zarejestruj
            </router-link>
          </div>
        </template>

      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

export default {
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const mobileMenuOpen = ref(false)

    const logout = () => {
      userStore.logout()
      router.push('/')
      mobileMenuOpen.value = false
    }

    onMounted(() => {
      userStore.initStore()
      const token = userStore.user.access
      if (token) {
        // Ustaw nagłówek Authorization dla axios
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
      } else {
        axios.defaults.headers.common['Authorization'] = ''
      }
    })

    return {
      router,
      userStore,
      logout,
      mobileMenuOpen,
    }
  },
}
</script>

<style>
/* Opcjonalne dostosowanie stylów globalnych */
body {
  @apply bg-gray-100;
}
</style>
