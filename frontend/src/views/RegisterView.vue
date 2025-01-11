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
            v-model="username"
            type="text"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Twoja nazwa użytkownika"
          />
        </div>
        <!-- Email -->
        <div class="mb-4">
          <label for="email" class="block mb-2 text-sm font-medium text-gray-700">Email</label>
          <input
            id="email"
            v-model="email"
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
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Twoje hasło"
          />
        </div>
        <!-- Przycisk rejestracji -->
        <button
          type="submit"
          class="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Zarejestruj się
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: "",
      email: "",
      password: "",
    };
  },
  methods: {
    register() {
      console.log("Dane rejestracyjne:", {
        username: this.username,
        email: this.email,
        password: this.password,
      });
      // Tu możesz dodać logikę rejestracji (np. wysłanie danych na backend)
    },
  },
};
</script>
