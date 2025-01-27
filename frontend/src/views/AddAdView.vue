<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-2xl p-6 bg-white rounded shadow-md">
      <h2 class="mb-6 text-2xl font-bold text-center text-blue-600">Dodaj ogłoszenie</h2>
      <form @submit.prevent="addAd">
        <div class="mb-4">
          <label for="title" class="block mb-2 text-sm font-medium text-gray-700">Tytuł ogłoszenia</label>
          <input
            id="title"
            v-model="form.tytul"
            type="text"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz tytuł ogłoszenia"
          />
        </div>
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700">Opis</label>
          <textarea
            id="description"
            v-model="form.opis"
            required
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz opis ogłoszenia"
          ></textarea>
        </div>
        <div class="mb-4">
          <label for="price" class="block mb-2 text-sm font-medium text-gray-700">Cena (w PLN)</label>
          <input
            id="price"
            v-model="form.cena"
            type="number"
            min="0"
            step="0.01"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Wpisz cenę"
          />
        </div>
        <div class="mb-4">
          <label for="category" class="block mb-2 text-sm font-medium text-gray-700">Kategoria</label>
          <select
            id="category"
            v-model="form.kategoria_id"
            required
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          >
            <option value="" disabled>Wybierz kategorię</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
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

<script setup>
import {ref, onMounted, onBeforeMount, reactive} from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const form = reactive({
  tytul: '',
  opis: '',
  cena: '',
  kategoria_id: '',
  email: userStore.user.email
})
const categories = ref([]);

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/');
    categories.value = response.data;

  } catch (error) {
    console.error('Błąd podczas pobierania kategorii:', error);
  }
};

const addAd = async () => {
  try {
    if (!form.kategoria_id) {
      form.kategoria_id = 1; // Możesz zmienić '1' na domyślną kategorię, którą chcesz ustawić
    }
    axios.defaults.headers.common["Authorization"] = "Bearer " + userStore.user.access;

    console.log(form)
    const response = await axios.post('/api/add_ad/', form);

    alert('Ogłoszenie zostało dodane');
  } catch (error) {
    console.error('Błąd podczas dodawania ogłoszenia:', error);
    alert('Nie udało się dodać ogłoszenia');
  }
};


onBeforeMount(async () => {
  try {
    await userStore.initStore();
    await fetchCategories();
    window.scrollTo(0, 0);
  } catch (error) {
    console.error('Błąd podczas inicjalizacji:', error);
  }
});
</script>