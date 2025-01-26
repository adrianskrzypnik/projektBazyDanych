<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-6 bg-white rounded shadow-md">
      <h2 class="mb-6 text-2xl font-bold text-center text-blue-600">Zaloguj się</h2>
      <form @submit.prevent="submitForm">
        <!-- Email -->
        <div class="mb-4">
          <label for="email" class="block mb-2 text-sm font-medium text-gray-700">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Twój email"
            :disabled="isLoading"
          />
        </div>
        <!-- Hasło -->
        <div class="mb-4">
          <label for="password" class="block mb-2 text-sm font-medium text-gray-700">Hasło</label>
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
              placeholder="Twoje hasło"
              :disabled="isLoading"
            />
            <button
              type="button"
              @click="togglePasswordVisibility"
              class="absolute right-2 top-1/2 transform -translate-y-1/2"
              :disabled="isLoading"
            >
              <EyeIcon v-if="showPassword" class="h-5 w-5 text-gray-500" />
              <EyeOffIcon v-else class="h-5 w-5 text-gray-500" />
            </button>
          </div>
        </div>
        <!-- Error Messages -->
        <div v-if="errors.length > 0" class="mb-4 text-red-600">
          <ul>
            <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
          </ul>
        </div>
        <!-- Przycisk logowania -->
        <button
          type="submit"
          class="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-blue-400"
          :disabled="isLoading"
        >
          <span v-if="isLoading">Logowanie...</span>
          <span v-else>Zaloguj się</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { EyeIcon, EyeOffIcon } from 'lucide-vue-next'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()

const form = reactive({
  email: '',
  password: ''
})


const errors = ref([])
const isLoading = ref(false)
const showPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const submitForm = async () => {
  errors.value = []
  isLoading.value = true

  if (form.email === '') {
    errors.value.push('Twój e-mail jest wymagany')
  }

  if (form.password === '') {
    errors.value.push('Twoje hasło jest wymagane')
  }

  if (errors.value.length === 0) {
    try {
      console.log(form)
      const response = await axios.post('/api/login/', form)
      axios.defaults.headers.common["Authorization"] = "Bearer " + response.data.access
      const userResponse = await axios.get('/api/me/')
      userStore.setUserInfo(userResponse.data)
      router.push('/')
    } catch (error) {
      console.error('Login error:', error)
      errors.value.push('E-mail lub hasło jest nieprawidłowe lub konto nie zostało aktywowane!')
    } finally {
      isLoading.value = false
    }
  }
}
</script>