<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-6 bg-white rounded shadow-md">
      <h2 class="mb-6 text-2xl font-bold text-center text-blue-600">Zarejestruj się</h2>
      <form @submit.prevent="register">
        <!-- Nazwa użytkownika -->
        <div class="mb-4">
          <label for="username" class="block mb-2 text-sm font-medium text-gray-700">Nazwa użytkownika</label>
          <input
            id="username"
            v-model="form.nazwa"
            type="text"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Twoja nazwa użytkownika"
          />
          <span v-if="errors.nazwa" class="text-red-500 text-xs mt-1">{{ errors.nazwa }}</span>
        </div>
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
          />
        </div>
        <!-- Hasło -->
        <div class="mb-4">
          <label for="password" class="block mb-2 text-sm font-medium text-gray-700">Hasło</label>
          <input
            id="password"
            v-model="form.haslo"
            type="password"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Twoje hasło"
          />
          <span v-if="errors.haslo" class="text-red-500 text-xs mt-1">{{ errors.haslo }}</span>
        </div>
        <!-- Przycisk rejestracji -->
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          Zarejestruj się
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

// Reactive form object
const form = reactive({
  nazwa: '',
  email: '',
  haslo: ''
});

// Error messages object
const errors = reactive({
  nazwa: '',
  haslo: ''
});

const isSubmitting = ref(false);

const validateForm = () => {
  let isValid = true;

  // Walidacja nazwy użytkownika
  if (form.nazwa.length < 3 || form.nazwa.length > 50) {
    errors.nazwa = 'Nazwa użytkownika musi mieć od 3 do 50 znaków.';
    isValid = false;
  } else {
    errors.nazwa = '';
  }

  // Walidacja hasła
  if (form.haslo.length < 8) {
    errors.haslo = 'Hasło musi mieć co najmniej 8 znaków.';
    isValid = false;
  } else {
    errors.haslo = '';
  }

  return isValid;
};

const register = async () => {
  if (!validateForm()) {
    return;
  }

  try {
    isSubmitting.value = true;
    const response = await axios.post('/api/register/', form);

    if (response.status === 201) {
      alert('Rejestracja przebiegła pomyślnie!');
      router.push('/login');  // Przekierowanie na stronę logowania
    } else {
      alert(response.data.error || 'Wystąpił błąd podczas rejestracji.');
    }
  } catch (error) {
    console.error('Błąd rejestracji:', error);
    alert('Wystąpił błąd. Spróbuj ponownie później.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>
