<template>
  <div class="p-6">
    <h1 class="text-4xl font-bold text-blue-600 mb-6">Panel Administracyjny</h1>

    <!-- Zakładki -->
    <div class="flex space-x-4 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="{
          'bg-blue-600 text-white': activeTab === tab,
          'bg-gray-200 text-gray-700': activeTab !== tab,
        }"
        class="px-4 py-2 rounded"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Treść zakładek -->
    <div v-if="activeTab === 'Użytkownicy'" class="bg-white p-4 rounded shadow-md">
      <h2 class="text-2xl font-semibold mb-4">Zarządzanie użytkownikami</h2>
      <table class="w-full table-auto mb-4 border-collapse border border-gray-300">
        <thead>
          <tr>
            <th class="border border-gray-300 px-4 py-2">Nazwa użytkownika</th>
            <th class="border border-gray-300 px-4 py-2">Email</th>
            <th class="border border-gray-300 px-4 py-2">Akcja</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td class="border border-gray-300 px-4 py-2">{{ user.username }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ user.email }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <button
                @click="toggleUserStatus(user)"
                :class="{
                  'bg-green-600 hover:bg-green-700': !user.isActive,
                  'bg-red-600 hover:bg-red-700': user.isActive,
                }"
                class="px-4 py-2 text-white rounded"
              >
                {{ user.isActive ? "Dezaktywuj" : "Aktywuj" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <Pagination :current-page="currentUserPage" :total-items="users.length" @page-changed="changeUserPage" />
    </div>

    <div v-if="activeTab === 'Kategorie'" class="bg-white p-4 rounded shadow-md">
      <h2 class="text-2xl font-semibold mb-4">Zarządzanie kategoriami</h2>
      <form @submit.prevent="addCategory" class="flex items-center mb-4">
        <input
          v-model="newCategory"
          type="text"
          placeholder="Nowa kategoria"
          class="flex-grow p-2 border border-gray-300 rounded"
        />
        <button
          type="submit"
          class="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Dodaj
        </button>
      </form>
      <table class="w-full table-auto mb-4 border-collapse border border-gray-300">
        <thead>
          <tr>
            <th class="border border-gray-300 px-4 py-2">Nazwa kategorii</th>
            <th class="border border-gray-300 px-4 py-2">Akcja</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in paginatedCategories" :key="category.id">
            <td class="border border-gray-300 px-4 py-2">{{ category.name }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <button
                @click="editCategory(category)"
                class="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
              >
                Edytuj
              </button>
              <button
                @click="deleteCategory(category.id)"
                class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Usuń
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <Pagination :current-page="currentCategoryPage" :total-items="categories.length" @page-changed="changeCategoryPage" />
    </div>

    <div v-if="activeTab === 'Logi'" class="bg-white p-4 rounded shadow-md">
      <h2 class="text-2xl font-semibold mb-4">Logi</h2>
      <ul>
        <li v-for="log in paginatedLogs" :key="log.id" class="text-sm text-gray-600 border-b py-1">
          {{ log.timestamp }} - {{ log.message }}
        </li>
      </ul>
      <Pagination :current-page="currentLogPage" :total-items="logs.length" @page-changed="changeLogPage" />
    </div>
  </div>
</template>

<script>
import Pagination from "@/components/Pagination.vue"; // Reusable component for paginacja

export default {
  data() {
    return {
      tabs: ["Użytkownicy", "Kategorie", "Logi"],
      activeTab: "Użytkownicy",

      // Użytkownicy
      users: [
        /* Dane z backendu */
      ],
      currentUserPage: 1,
      itemsPerPage: 10,

      // Kategorie
      categories: [
        /* Dane z backendu */
      ],
      currentCategoryPage: 1,

      // Logi
      logs: [
        /* Dane z backendu */
      ],
      currentLogPage: 1,

      newCategory: "",
    };
  },
  computed: {
    paginatedUsers() {
      return this.paginate(this.users, this.currentUserPage);
    },
    paginatedCategories() {
      return this.paginate(this.categories, this.currentCategoryPage);
    },
    paginatedLogs() {
      return this.paginate(this.logs, this.currentLogPage);
    },
  },
  methods: {
    paginate(items, page) {
      const start = (page - 1) * this.itemsPerPage;
      const end = page * this.itemsPerPage;
      return items.slice(start, end);
    },
    changeUserPage(page) {
      this.currentUserPage = page;
    },
    changeCategoryPage(page) {
      this.currentCategoryPage = page;
    },
    changeLogPage(page) {
      this.currentLogPage = page;
    },
    toggleUserStatus(user) {
      /* Logika aktywacji/dezaktywacji użytkownika */
    },
    addCategory() {
      /* Logika dodawania kategorii */
    },
    editCategory(category) {
      /* Logika edytowania kategorii */
    },
    deleteCategory(id) {
      /* Logika usuwania kategorii */
    },
  },
};
</script>

<style scoped>
/* Opcjonalne style */
</style>
