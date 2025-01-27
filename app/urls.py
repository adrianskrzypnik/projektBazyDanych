from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


urlpatterns = [
    #funckje api
    path('register/', views.zarejestruj_uzytkownika, name='register'),
    path('login/', views.zaloguj_uzytkownika, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('me/', views.me, name='me'),
    path('profile_stats/', views.pobierz_statystyki_profilu, name='me'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.wyloguj_uzytkownika, name='logout'),
    path('edit_profile/<int:user_id>/', views.edytuj_profil, name='edit_profile'),
    path('ad/<int:ad_id>/', views.get_ad_details, name='get_ad_details'),
    path('add_ad/', views.dodaj_ogloszenie, name='add_ad'),
    path('delete_ad/<int:ad_id>/', views.usun_ogloszenie, name='delete_ad'),
    path('edit_ad/<int:ad_id>/', views.edytuj_ogloszenie, name='edit_ad'),
    path('discover_ads/', views.przegladaj_ogloszenia, name='discover_ads'),
    path('add_comment/', views.dodaj_komentarz, name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.edytuj_komentarz, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.usun_komentarz, name='delete_comment'),
    path('like/', views.polub, name='like'),
    path('dislike/<int:like_id>/', views.usun_polubienie, name='dislike'),
    path('rate_user/<int:oceniany_id>/', views.ocen_uzytkownika, name='rate_user'),
    path('deactivate_user/<int:user_id>/', views.dezaktywuj_uzytkownika, name='deactivate_user'),
    path('activate_user/<int:user_id>/', views.aktywuj_uzytkownika, name='activate_user'),
    path('add_category/', views.stworz_kategorie, name='add_category'),
    path('categories/', views.pobierz_kategorie, name='categories'),
    path('edit_category/<int:category_id>/', views.edytuj_kategorie, name='edit_category'),
    path('delete_category/<int:category_id>/', views.usun_kategorie, name='delete_category'),
    path('show_logs/', views.pokaz_logi, name='show_logs'),


]