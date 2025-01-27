<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <!-- Dane użytkownika -->
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-2xl font-bold text-blue-600">Profil użytkownika</h2>
      <div class="flex flex-col sm:flex-row justify-between mt-4">
        <div>
          <p><strong>Nazwa użytkownika:</strong> {{ userStore.user.name }}</p>
          <p><strong>Email:</strong> {{ userStore.user.email }}</p>
          <p><strong>Polubienia:</strong> {{stats.likes_count}}</p>
          <p><strong>Ocena:</strong> {{stats.average_rating}}</p>
        </div>
        <div class="mt-4 sm:mt-0">
          <button
            @click="toggleEditProfile"
            class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {{ isEditingProfile ? "Anuluj edycję" : "Edytuj profil" }}
          </button>
        </div>

      </div>


      <!-- Edycja profilu -->
      <div v-if="isEditingProfile" class="mt-6">
        <form @submit.prevent="updateProfile">
          <div class="mb-4">
            <label for="username" class="block mb-2 text-sm font-medium text-gray-700">Nazwa użytkownika</label>
            <input
              id="username"
              v-model="editedUser.username"
              :placeholder="userStore.user.name"
              type="text"
              class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            />
          </div>
          <div class="mb-4">
            <label for="email" class="block mb-2 text-sm font-medium text-gray-700">Email</label>
            <input
              id="email"
              v-model="editedUser.email"
              :placeholder="userStore.user.email"
              type="email"
              class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
            />
          </div>
          <button
            type="submit"
            class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700"
          >
            Zapisz zmiany
          </button>
        </form>
      </div>




    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeMount, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';

const userStore = useUserStore();
const router = useRouter();

const isEditingProfile = ref(false);

const stats = ref({
  likes_count: 0,
  comments_count: 0,
  average_rating: 0.0,
});

const editedUser = reactive({
  username: '',
  email: ''
});


const fetchProfileStats = async () => {
  console.log('Pobieram statystyki profilu');
  try {
    axios.defaults.headers.common["Authorization"] = "Bearer " + userStore.user.access;
    const response = await axios.get('/api/profile_stats/');
    stats.value = response.data;
  } catch (error) {
    console.error('Błąd podczas pobierania statystyk profilu:', error);
  }
};

const toggleEditProfile = () => {
  isEditingProfile.value = !isEditingProfile.value;
};

const updateProfile = async () => {
  try {
    axios.defaults.headers.common["Authorization"] = "Bearer " + userStore.user.access;
    const response = await axios.post(`/api/edit_profile/${userStore.user.user_id}/`, {
      nazwa: editedUser.username || userStore.user.name,
      email: editedUser.email || userStore.user.email
    });

    // Zaktualizuj dane w store
    userStore.user.name = editedUser.username || userStore.user.name;
    userStore.user.email = editedUser.email || userStore.user.email;

    isEditingProfile.value = false;
  } catch (error) {
    console.error('Błąd podczas aktualizacji profilu:', error);
  }
};

onBeforeMount(async () => {
  try {
    await userStore.initStore();
    await fetchProfileStats();
    window.scrollTo(0, 0);
  } catch (error) {
    console.error('Błąd podczas inicjalizacji:', error);
  }
});



</script>

<style scoped>
/* Dodatkowe style opcjonalne */
</style>
