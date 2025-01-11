<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-2xl p-6 bg-white rounded shadow-md">
      <h2 class="mb-6 text-2xl font-bold text-center text-blue-600">Dodaj ogłoszenie</h2>
      <form @submit.prevent="addAd">
        <!-- Tytuł -->
        <div class="mb-4">
          <label for="title" class="block mb-2 text-sm font-medium text-gray-700">Tytuł ogłoszenia</label>
          <input
            id="title"
            v-model="title"
            type="text"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz tytuł ogłoszenia"
          />
        </div>
        <!-- Opis -->
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700">Opis</label>
          <textarea
            id="description"
            v-model="description"
            required
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz opis ogłoszenia"
          ></textarea>
        </div>
        <!-- Cena -->
        <div class="mb-4">
          <label for="price" class="block mb-2 text-sm font-medium text-gray-700">Cena (w PLN)</label>
          <input
            id="price"
            v-model="price"
            type="number"
            min="0"
            step="0.01"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz cenę"
          />
        </div>
        <!-- Kategoria -->
        <div class="mb-4">
          <label for="category" class="block mb-2 text-sm font-medium text-gray-700">Kategoria</label>
          <select
            id="category"
            v-model="category"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          >
            <option value="" disabled>Wybierz kategorię</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <!-- Przycisk dodawania -->
        <button
          type="submit"
          class="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Dodaj ogłoszenie
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      title: "",
      description: "",
      price: "",
      category: "",
      categories: [], // Lista kategorii
    };
  },
  methods: {
    addAd() {
      console.log("Dodawanie ogłoszenia:", {
        title: this.title,
        description: this.description,
        price: this.price,
        category: this.category,
      });
      // Tutaj można dodać logikę wysyłania danych na backend
    },
    async fetchCategories() {
      try {
        // Symulacja pobierania kategorii z backendu
        // Później podmień na rzeczywiste API
        this.categories = [
          { id: 1, name: "Elektronika" },
          { id: 2, name: "Samochody" },
          { id: 3, name: "Nieruchomości" },
          { id: 4, name: "Moda" },
          { id: 5, name: "Sport" },
        ];
      } catch (error) {
        console.error("Błąd podczas pobierania kategorii:", error);
      }
    },
  },
  mounted() {
    this.fetchCategories();
  },
};
</script>
