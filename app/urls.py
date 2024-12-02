from django.urls import path
from . import views

urlpatterns = [
    path('zarejestruj/', views.zarejestruj_uzytkownika, name='zarejestruj'),
]