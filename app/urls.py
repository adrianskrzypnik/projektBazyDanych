from django.urls import path
from . import views
ą
urlpatterns = [
    #funckje api
    path('register/', views.zarejestruj_uzytkownika, name='register'),
    path('login/', views.zaloguj_uzytkownika, name='login'),
    path('logout/', views.wyloguj_uzytkownika, name='logout'),
    path('edit_profile/<int:user_id>/', views.edytuj_profil, name='edit_profile'),
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
    path('edit_category/<int:category_id>/', views.edytuj_kategorie, name='edit_category'),
    path('delete_category/<int:category_id>/', views.usun_kategorie, name='delete_category'),
    path('show_logs/', views.pokaz_logi, name='show_logs'),

    # html do testowania funkcji

    path('register/test/', views.zarejestruj_uzytkownika_test, name='register_test'),
    path('login/test/', views.zaloguj_uzytkownika_test, name='login_test'),
    path('logout/test/', views.wyloguj_uzytkownika_test, name='logout_test'),
    path('edit_profile/<int:user_id>/test/', views.edytuj_profil_test, name='edit_profile_test'),
    path('add_ad/test/', views.dodaj_ogloszenie_test, name='add_ad_test'),
    path('delete_ad/<int:ad_id>/test/', views.usun_ogloszenie_test, name='delete_ad_test'),
    path('edit_ad/<int:ad_id>/test/', views.edytuj_ogloszenie_test, name='edit_ad_test'),
    path('discover_ads/test/', views.przegladaj_ogloszenia_test, name='discover_ads_test'),
    path('add_comment/test/', views.dodaj_komentarz_test, name='add_comment_test'),
    path('edit_comment/<int:comment_id>/test/', views.edytuj_komentarz_test, name='edit_comment_test'),
    path('delete_comment/<int:comment_id>/test/', views.usun_komentarz_test, name='delete_comment_test'),
    path('like/test/', views.polub_test, name='like_test'),
    path('dislike/<int:like_id>/test/', views.usun_polubienie_test, name='dislike_test'),
    path('rate_user/<int:oceniany_id>/test/', views.ocen_uzytkownika_test, name='rate_user_test'),
    path('deactivate_user/<int:user_id>/test/', views.dezaktywuj_uzytkownika_test, name='deactivate_user_test'),
    path('activate_user/<int:user_id>/test/', views.aktywuj_uzytkownika_test, name='activate_user_test'),
    path('add_category/test/', views.stworz_kategorie_test, name='add_category_test'),
    path('edit_category/<int:category_id>/test/', views.edytuj_kategorie_test, name='edit_category_test'),
    path('delete_category/<int:category_id>/test/', views.usun_kategorie_test, name='delete_category_test'),

]