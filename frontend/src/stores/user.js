import { defineStore } from "pinia";
import axios from 'axios';

export const useUserStore = defineStore({
    id: 'user',
    state: () => ({
        user: {
            isAuthenticated: false,
            user_id: null,
            name: null,
            email: null,
            is_staff: false,
            is_active: false,
            access: null,
            refresh: null,
        },
        loading: false,
        error: null
    }),
    actions: {
        async initStore() {
            if (localStorage.getItem('user.access')) {
                this.user.access = localStorage.getItem('user.access');
                this.user.refresh = localStorage.getItem('user.refresh');
                this.user.isAuthenticated = true;

                try {
                    const response = await axios.get('/api/me/', {
                        headers: {
                            Authorization: `Bearer ${this.user.access}`
                        }
                    });
                    this.setUserInfo(response.data);
                } catch (error) {
                    console.error('Failed to fetch user info:', error);
                    this.removeToken();
                }

                this.refreshToken();
            }
        },
        setToken(data) {
            this.user.access = data.access;
            this.user.refresh = data.refresh;
            this.user.isAuthenticated = true;
            localStorage.setItem('user.access', data.access);
            localStorage.setItem('user.refresh', data.refresh);
            console.log(this.user)
        },
        removeToken() {
            this.user.isAuthenticated = false;
            this.user.access = null;
            this.user.refresh = null;
            this.user.user_id = null;
            this.user.name = null;
            this.user.email = null;
            this.user.is_staff = false;
            localStorage.clear();
        },
        setUserInfo(user) {

            this.user.user_id = user.user_id;
            this.user.name = user.name;
            this.user.email = user.email;
            this.user.is_staff = user.is_staff;
            localStorage.setItem('user.user_id', user.user_id);
            localStorage.setItem('user.name', user.name);
            localStorage.setItem('user.email', user.email);
            localStorage.setItem('user.is_staff', user.is_staff);
        },
        refreshToken() {
            axios.post('/api/refresh/', {
                refresh: this.user.refresh
            })
            .then((response) => {
                this.user.access = response.data.access;
                localStorage.setItem('user.access', response.data.access);
                axios.defaults.headers.common["Authorization"] = "Bearer " + response.data.access;
            })
            .catch(() => {
                this.removeToken();
            });
        },
        logout() {
            this.removeToken();
        },
    }
});
