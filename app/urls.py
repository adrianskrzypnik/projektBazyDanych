from django.urls import path
from . import views

urlpatterns = [
    #funckje api
    path('register/', views.zarejestruj_uzytkownika, name='register'),
    path('login/', views.zaloguj_uzytkownika, name='login'),
    path('edit_profile/', views.edytuj_profil, name='edit_profile'),
    path('add_ad/', views.dodaj_ogloszenie, name='add_ad'),
    path('delete_ad/<int:ad_id>', views.usun_ogloszenie, name='delete_ad'),
    path('edit_ad/<int:ad_id>/', views.edytuj_ogloszenie, name='edit_ad'),
    path('discover_ads/', views.przegladaj_ogloszenia, name='discover_ads'),
    path('add_comment/<int:ad_id>/', views.dodaj_komentarz, name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.edytuj_komentarz, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.usun_komentarz, name='delete_comment'),
    path('like_ad/<int:ad_id>/', views.polub_ogloszenie, name='like_ad'),
    path('dislike_ad/<int:ad_id>/', views.usun_polubienie, name='dislike_ad'),
    path('rate_user/<int:oceniany_id>/', views.ocen_uzytkownika, name='rate_user'),

    # html do testowania funkcji

    path('register/test/', views.zarejestruj_uzytkownika_test, name='register_test'),
    path('login/test/', views.zaloguj_uzytkownika_test, name='login_test'),
    path('edit_profile/test/', views.edytuj_profil_test, name='edit_profile_test'),
    path('add_ad/test/', views.dodaj_ogloszenie_test, name='add_ad_test'),
    path('delete_ad/<int:ad_id>/test', views.usun_ogloszenie_test, name='delete_ad_test'),
    path('edit_ad/<int:ad_id>/test/', views.edytuj_ogloszenie_test, name='edit_ad_test'),
    path('discover_ads/test/', views.przegladaj_ogloszenia_test, name='discover_ads_test'),
    path('add_comment/<int:ad_id>/test/', views.dodaj_komentarz_test, name='add_comment_test'),
    path('edit_comment/<int:comment_id>/test/', views.edytuj_komentarz_test, name='edit_comment_test'),
    path('delete_comment/<int:comment_id>/test/', views.usun_komentarz_test, name='delete_comment_test'),
    path('like_ad/<int:ad_id>/test/', views.polub_ogloszenie_test, name='like_ad_test'),
    path('dislike_ad/<int:ad_id>/test/', views.usun_polubienie_test, name='dislike_ad_test'),
    path('rate_user/<int:oceniany_id>/test/', views.ocen_uzytkownika_test, name='rate_user_test'),


]