<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-md">
      <div class="container mx-auto flex items-center justify-between p-4">
        <!-- Logo -->
        <div class="text-xl font-bold text-blue-600">
          Portal OLY
        </div>
        <!-- Buttons -->
        <div class="space-x-4">
          <button
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
          >
            Zaloguj
          </button>
          <button
            class="px-4 py-2 text-sm font-medium text-blue-600 border border-blue-600 rounded hover:bg-blue-100"
          >
            Zarejestruj
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
/* Opcjonalne dostosowanie stylów globalnych */
body {
  @apply bg-gray-100;
}
</style>
