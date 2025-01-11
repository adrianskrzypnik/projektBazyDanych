<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-6 bg-white rounded shadow-md">
      <h2 class="mb-6 text-2xl font-bold text-center text-blue-600">Zaloguj się</h2>
      <form @submit.prevent="login">
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
        <!-- Przycisk logowania -->
        <button
          type="submit"
          class="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Zaloguj się
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
    };
  },
  methods: {
    login() {
      console.log("Dane logowania:", {
        email: this.email,
        password: this.password,
      });
      // Tu możesz dodać logikę logowania (np. wysłanie danych na backend)
    },
  },
};
</script>
