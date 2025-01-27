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
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
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
        v-for="ad in ads"
        :key="ad.ad_id"
        class="p-4 bg-white rounded shadow-md hover:shadow-lg"
      >
        <h3 class="text-lg font-semibold text-blue-600 mb-2">{{ ad.tytul }}</h3>
        <p class="text-gray-700 mb-2"><strong>Cena:</strong> {{ ad.cena }} PLN</p>
        <p class="text-gray-700 mb-4"><strong>Kategoria:</strong>
          {{ getCategoryName(ad.kategoria_id) }}
        </p>
        <p class="text-gray-600 mb-4">{{ ad.opis }}</p>
        <router-link
          :to="`/ad/${ad.ad_id}`"
          class="text-blue-600 hover:underline"
        >
          Zobacz szczegóły
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onBeforeMount } from 'vue';
import axios from 'axios';
import { useUserStore } from "@/stores/user.js";

const userStore = useUserStore();

const filters = reactive({
  category: '',
  priceMin: null,
  priceMax: null,
});

const ads = ref([]);
const categories = ref([]);

// Funkcja pobierająca kategorie z API
const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/');
    categories.value = response.data;
  } catch (error) {
    console.error('Błąd podczas pobierania kategorii:', error);
  }
};

// Funkcja pobierająca ogłoszenia
const fetchAds = async () => {
  try {
    const requestData = {
      category: filters.category || null,
      min_price: filters.priceMin || null,
      max_price: filters.priceMax || null
    };

    const response = await axios.get('/api/discover_ads/', {
      params: requestData
    });

    if (response.data && response.data.ads) {
      ads.value = response.data.ads;
    }
  } catch (error) {
    console.error('Błąd podczas ładowania ogłoszeń:', error);
  }
};

// Funkcja do znalezienia nazwy kategorii na podstawie kategoria_id
const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId);
  return category ? category.name : 'Brak kategorii';
};

// Funkcja wywoływana po kliknięciu przycisku "Filtruj"
const applyFilters = async () => {
  await fetchAds();
};

// Inicjalizacja komponentu
onBeforeMount(async () => {
  await userStore.initStore();
  await fetchCategories();
  await fetchAds();
});
</script>