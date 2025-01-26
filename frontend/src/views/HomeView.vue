<template>
  <div class="p-6">
    <h1 class="text-4xl font-bold text-blue-600 mb-6">Portal OLY - Ogłoszenia</h1>

    <!-- Sekcja filtrowania -->
    <div class="bg-white p-4 mb-6 rounded shadow-md">
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">Filtruj ogłoszenia</h2>
      <form @submit.prevent="applyFilters" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Kategoria -->
        <div>
          <label for="category" class="block text-gray-700 mb-2">Kategoria</label>
          <select
            id="category"
            v-model="filters.category"
            class="w-full p-2 border border-gray-300 rounded"
          >
            <option value="">Wszystkie</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>

        <!-- Cena minimalna -->
        <div>
          <label for="price-min" class="block text-gray-700 mb-2">Cena minimalna</label>
          <input
            type="number"
            id="price-min"
            v-model.number="filters.priceMin"
            class="w-full p-2 border border-gray-300 rounded"
            placeholder="0"
          />
        </div>

        <!-- Cena maksymalna -->
        <div>
          <label for="price-max" class="block text-gray-700 mb-2">Cena maksymalna</label>
          <input
            type="number"
            id="price-max"
            v-model.number="filters.priceMax"
            class="w-full p-2 border border-gray-300 rounded"
            placeholder="0"
          />
        </div>

        <!-- Przycisk filtruj -->
        <div class="md:col-span-3 text-right">
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Filtruj
          </button>
        </div>
      </form>
    </div>

    <!-- Lista ogłoszeń -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="ad in filteredAds"
        :key="ad.id"
        class="p-4 bg-white rounded shadow-md hover:shadow-lg"
      >
        <h3 class="text-lg font-semibold text-blue-600 mb-2">{{ ad.title }}</h3>
        <p class="text-gray-700 mb-2"><strong>Kategoria:</strong> {{ ad.category }}</p>
        <p class="text-gray-700 mb-4"><strong>Cena:</strong> {{ ad.price }} PLN</p>
        <p class="text-gray-600 mb-4">{{ ad.description }}</p>
        <router-link
          :to="`/ads/${ad.id}`"
          class="text-blue-600 hover:underline"
        >
          Zobacz szczegóły
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // Lista ogłoszeń (do zastąpienia danymi z backendu)
      ads: [
        { id: 1, title: "Ogłoszenie 1", category: "Elektronika", price: 500, description: "Opis ogłoszenia 1" },
        { id: 2, title: "Ogłoszenie 2", category: "Meble", price: 200, description: "Opis ogłoszenia 2" },
        { id: 3, title: "Ogłoszenie 3", category: "Motoryzacja", price: 3000, description: "Opis ogłoszenia 3" },
        { id: 4, title: "Ogłoszenie 4", category: "Nieruchomości", price: 500000, description: "Opis ogłoszenia 4" },
      ],

      // Kategorie (do zastąpienia danymi z backendu)
      categories: ["Elektronika", "Meble", "Motoryzacja", "Nieruchomości"],

      // Filtry
      filters: {
        category: "",
        priceMin: 0,
        priceMax: 0,
      },
    };
  },
  computed: {
    // Filtrowane ogłoszenia
    filteredAds() {
      return this.ads.filter((ad) => {
        const categoryMatch = !this.filters.category || ad.category === this.filters.category;
        const priceMinMatch = !this.filters.priceMin || ad.price >= this.filters.priceMin;
        const priceMaxMatch = !this.filters.priceMax || ad.price <= this.filters.priceMax;
        return categoryMatch && priceMinMatch && priceMaxMatch;
      });
    },
  },
  methods: {
    applyFilters() {
      // Ewentualna logika dodatkowa dla filtrowania
      console.log("Filtry zastosowane:", this.filters);
    },
  },
};
</script>

<style scoped>
/* Opcjonalne style */
</style>
