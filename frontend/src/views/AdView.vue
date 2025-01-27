<template>
  <div class="flex flex-col items-center min-h-screen bg-gray-100">
    <!-- Szczegóły ogłoszenia -->
    <div class="w-full max-w-4xl p-6 mt-8 bg-white rounded shadow-md">
      <h2 class="mb-4 text-3xl font-bold text-blue-600">{{ ad.title }}</h2>
      <p class="mb-2 text-gray-700"><strong>Kategoria:</strong> {{ ad.category }}</p>
      <p class="mb-2 text-gray-700"><strong>Cena:</strong> {{ ad.price }} PLN</p>
      <p class="mb-4 text-gray-700"><strong>Opis:</strong> {{ ad.description }}</p>
      <div class="flex items-center justify-between">
        <!-- Polubienia i licznik -->
        <div class="flex items-center space-x-4">
          <button
            @click="likeAd"
            class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Polub
          </button>
          <span class="text-gray-700">{{ ad.likes_count }} Polubień</span>
        </div>

        <!-- Przycisk edycji maksymalnie po prawej stronie -->
        <button
          v-if="canEdit"
          @click="toggleEdit"
          class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          {{ isEditing ? "Anuluj edycję" : "Edytuj ogłoszenie" }}
        </button>
      </div>
    </div>




    <!-- Formularz edycji -->
    <div
      v-if="isEditing"
      class="w-full max-w-4xl p-6 mt-6 bg-white rounded shadow-md"
    >
      <h3 class="mb-4 text-xl font-bold text-blue-600">Edytuj ogłoszenie</h3>
      <form @submit.prevent="updateAd">
        <!-- Tytuł -->
        <div class="mb-4">
          <label for="title" class="block mb-2 text-sm font-medium text-gray-700">Tytuł</label>
          <input
            id="title"
            v-model="ad.title"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          />
        </div>
        <!-- Opis -->
        <div class="mb-4">
          <label for="description" class="block mb-2 text-sm font-medium text-gray-700">Opis</label>
          <textarea
            id="description"
            v-model="ad.description"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          ></textarea>
        </div>
        <!-- Cena -->
        <div class="mb-4">
          <label for="price" class="block mb-2 text-sm font-medium text-gray-700">Cena</label>
          <input
            id="price"
            v-model="ad.price"
            type="number"
            min="0"
            step="0.01"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          />
        </div>
        <!-- Kategoria -->
        <div class="mb-4">
          <label for="category" class="block mb-2 text-sm font-medium text-gray-700">Kategoria</label>
          <select
            id="category"
            v-model="ad.category"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          >
            <option value="" disabled>Wybierz kategorię</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
          </select>
        </div>
        <button
          type="submit"
          class="w-full px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Zaktualizuj ogłoszenie
        </button>
      </form>
    </div>

    <!-- Komentarze -->
    <div class="w-full max-w-4xl p-6 mt-6 bg-white rounded shadow-md">
      <h3 class="text-xl font-bold text-blue-600">Komentarze</h3>
      <div v-if="comments.length" class="mt-4">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="p-4 mb-4 bg-gray-100 rounded-lg"
        >
          <p><strong>{{ comment.author }}:</strong></p>
          <p>{{ comment.content }}</p>
        </div>
      </div>
      <p v-else class="text-gray-600">Brak komentarzy.</p>

      <!-- Dodawanie komentarza -->
      <form @submit.prevent="addComment" class="mt-6">
        <textarea
          v-model="newComment"
          placeholder="Dodaj komentarz..."
          class="w-full p-4 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
        ></textarea>
        <button
          type="submit"
          class="mt-4 px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Dodaj komentarz
        </button>
      </form>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeMount, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';

const route = useRoute();
const userStore = useUserStore();

const ad = ref({
  title: '',
  description: '',
  price: 0,
  category: '',
  author: '',
  likes_count: ''
});
const comments = ref([]);
const likes = ref(0);
const newComment = ref('');
const isEditing = ref(false);
const categories = ref([]);

// Sprawdzanie czy użytkownik może edytować ogłoszenie
const canEdit = computed(() => {
  return userStore.user && userStore.user.id === ad.value.author_id;
});

// Pobieranie danych ogłoszenia
const fetchAdDetails = async () => {
  try {
    const response = await axios.get(`/api/ad/${route.params.id}/`);
    ad.value = response.data.ad;
    comments.value = response.data.comments;
    likes.value = response.data.ad.likes_count;
  } catch (error) {
    console.error('Błąd podczas pobierania szczegółów ogłoszenia:', error);
  }
};

// Pobieranie kategorii (potrzebne do edycji)
const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories/');
    categories.value = response.data;
  } catch (error) {
    console.error('Błąd podczas pobierania kategorii:', error);
  }
};

// Dodawanie komentarza
const addComment = async () => {
  if (!newComment.value.trim()) return;

  try {
    const response = await axios.post('/api/add_comment/', {
      type: 'ad',  // Typ - komentarz do ogłoszenia
      id: route.params.id,  // ID ogłoszenia (z URL)
      content: newComment.value,  // Treść komentarza
    });
    comments.value.push({
      author: 'Zalogowany użytkownik',  // Tu możesz podać dane użytkownika
      text: newComment.value,
    });
    newComment.value = '';  // Wyczyść pole komentarza
  } catch (error) {
    console.error('Błąd podczas dodawania komentarza:', error);
  }
};

// Polubienie ogłoszenia
const likeAd = async () => {
  try {
    await axios.post(`/api/ad/${route.params.id}/like/`);
    likes.value += 1;
  } catch (error) {
    console.error('Błąd podczas dodawania polubienia:', error);
  }
};

// Przełączanie trybu edycji
const toggleEdit = () => {
  isEditing.value = !isEditing.value;
};

// Aktualizacja ogłoszenia
const updateAd = async () => {
  try {
    await axios.put(`/api/ad/${route.params.id}/`, {
      title: ad.value.title,
      description: ad.value.description,
      price: ad.value.price,
      category: ad.value.category
    });
    isEditing.value = false;
    await fetchAdDetails();
  } catch (error) {
    console.error('Błąd podczas aktualizacji ogłoszenia:', error);
  }
};

onBeforeMount(async () => {
  await userStore.initStore();
  await fetchCategories();
  await fetchAdDetails();
});
</script>
