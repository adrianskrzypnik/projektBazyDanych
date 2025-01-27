from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
import re
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from .serializers import AuthTokenObtainPairSerializer

from .models import User

def validate_positive_float(value, field_name):
    try:
        value = float(value)
        if value < 0:
            raise ValidationError(f"{field_name} musi być liczbą dodatnią.")
        return value
    except ValueError:
        raise ValidationError(f"{field_name} musi być liczbą.")

def validate_string(value, field_name, max_length=255):
    if not value or not isinstance(value, str):
        raise ValidationError(f"{field_name} jest wymagany i musi być tekstem.")
    if len(value) > max_length:
        raise ValidationError(f"{field_name} nie może mieć więcej niż {max_length} znaków.")
    return escape(value)

def validate_integer(value, field_name):
    if not re.match(r'^\d+$', str(value)):
        raise ValidationError(f"{field_name} musi być liczbą całkowitą.")
    return int(value)





@api_view(['GET'])
def me(request):
    print(request.user)
    print(request.user.user_id)
    print(request.user.nazwa)
    print(request.user.email)
    return JsonResponse({
        'user_id': request.user.user_id,
        'name': request.user.nazwa,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def zaloguj_uzytkownika(request):
    if request.method == 'POST':
        email = request.data.get('email')
        haslo = request.data.get('password')
        ip_address = request.META.get('REMOTE_ADDR', '')

        # Zapis loga o próbie logowania
        zapisz_log(email, 'LOGOWANIE_PRÓBA', 'Próba logowania', ip_address)

        # Walidacja danych wejściowych
        if not email or not haslo:
            return JsonResponse({'error': 'Email i hasło są wymagane.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Nieprawidłowy format adresu email.'}, status=400)

        sql = "SELECT * FROM users WHERE email = %s"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [email])
                user = cursor.fetchone()

                if user:
                    # Sprawdzamy, czy hasło jest poprawne
                    if user[3] != haslo:  # Zakładając, że user[3] to hasło w bazie danych (kolumna 'haslo')
                        return JsonResponse({'error': 'Nieprawidłowe hasło.'}, status=400)

                    # Sprawdzamy, czy użytkownik jest aktywny
                    if not user[5]:  # Zakładając, że user[5] to pole 'is_active'
                        return JsonResponse({'error': 'Konto użytkownika jest nieaktywne.'}, status=400)

                    user_instance = User(
                        user_id = user[0],
                        nazwa=user[1],
                        email=user[2],
                        is_staff=user[6]
                    )

                    refresh = AuthTokenObtainPairSerializer.get_token(user_instance)

                    access_token = refresh.access_token

                    # Zapis loga o udanym logowaniu
                    zapisz_log(email, 'LOGOWANIE_SUKCES', 'Użytkownik zalogowany pomyślnie', ip_address)

                    # Zwracamy tokeny w odpowiedzi
                    return JsonResponse({
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }, status=200)

                # Jeśli użytkownik nie istnieje
                zapisz_log(email, 'LOGOWANIE_BŁĄD', 'Nieprawidłowy email lub hasło', ip_address)
                return JsonResponse({'error': 'Nieprawidłowy email lub hasło.'}, status=400)

        except Exception as e:
            # Zapis loga o błędzie logowania
            zapisz_log(email, 'LOGOWANIE_BŁĄD', f'Błąd logowania: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pobierz_statystyki_profilu(request):
    """
    Pobiera statystyki profilu użytkownika (liczba polubień, liczba komentarzy, średnia ocena).
    """
    user_id = request.user.user_id
    try:
        sql = """
            SELECT 
                likes_received_count,
                comments_received_count,
                average_rating
            FROM users
            WHERE user_id = %s
        """
        with connection.cursor() as cursor:

            cursor.execute(sql, [user_id])
            wynik = cursor.fetchone()

            if wynik:
                likes, comments, rating = wynik
                return JsonResponse({
                    'likes_count': likes or 0,
                    'comments_count': comments or 0,
                    'average_rating': rating or 0.0
                }, status=200)
            else:
                return JsonResponse({'error': 'Użytkownik nie istnieje.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': f'Wystąpił błąd: {str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST'])
def zarejestruj_uzytkownika(request):
    '''
    Funkcja rejestracji użytkownika ze sprawdzeniem czy podany mail nie jest już wykorzystany
    '''
    if request.method == 'POST':
        nazwa = request.data.get('nazwa')
        email = request.data.get('email')
        haslo = request.data.get('haslo')
        data_utworzenia = datetime.now()
        ip_address = request.META.get('REMOTE_ADDR', '')

        # Zapis loga o próbie rejestracji
        zapisz_log(email, 'REJESTRACJA_PRÓBA', f'Próba rejestracji użytkownika {nazwa}', ip_address)

        # Walidacja danych wejściowych
        if not nazwa or not email or not haslo:
            return JsonResponse({'error': 'Wszystkie pola są wymagane.'}, status=400)

        if len(nazwa) < 3 or len(nazwa) > 50:
            return JsonResponse({'error': 'Nazwa użytkownika musi mieć od 3 do 50 znaków.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Podano nieprawidłowy adres e-mail.'}, status=400)

        if len(haslo) < 8:
            return JsonResponse({'error': 'Hasło musi mieć co najmniej 8 znaków.'}, status=400)

        if not re.search(r'[A-Za-z]', haslo) or not re.search(r'[0-9]', haslo):
            return JsonResponse({'error': 'Hasło musi zawierać co najmniej jedną literę i jedną cyfrę.'}, status=400)

        check_email_sql = "SELECT COUNT(*) FROM users WHERE email = %s"
        insert_sql = """
        INSERT INTO users (nazwa, email, password, data_utworzenia)
        VALUES (%s, %s, %s, %s)
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(check_email_sql, [email])
                email_count = cursor.fetchone()[0]

                if email_count > 0:
                    # Zapis loga o próbie rejestracji istniejącego użytkownika
                    zapisz_log(email, 'REJESTRACJA_BŁĄD', 'Próba rejestracji istniejącego emaila', ip_address)
                    return JsonResponse(
                        {'error': 'Użytkownik z podanym adresem e-mail już istnieje.'},
                        status=400
                    )

                cursor.execute(insert_sql, [nazwa, email, haslo, data_utworzenia])

            # Zapis loga o udanej rejestracji
            zapisz_log(email, 'REJESTRACJA_SUKCES', 'Użytkownik zarejestrowany pomyślnie', ip_address)
            return JsonResponse({'message': 'Użytkownik został zarejestrowany.'}, status=201)

        except Exception as e:
            # Zapis loga o błędzie rejestracji
            zapisz_log(email, 'REJESTRACJA_BŁĄD', f'Błąd rejestracji: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=400)


def zarejestruj_uzytkownika_test(request):
    '''
    Funkcja do testownia funkcji api register
    '''
    return render(request, 'register.html')





def wyloguj_uzytkownika(request):
    '''
    Funkcja wylogowania użytkownika
    '''
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [request.session.get('user_id')])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    if request.method == 'POST':
        try:
            if 'user_id' in request.session:
                del request.session['user_id']

            request.session.flush()

            zapisz_log(email, 'WYLOGOWANIE_SUKCES', 'Użytkownik został wylogowany', ip_address)

            return JsonResponse({'message': 'Wylogowano pomyślnie.'}, status=200)
        except Exception as e:
            zapisz_log(email, 'WYLOGOWANIE_BŁĄD', f'Błąd wylogowania: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)

    zapisz_log(email, 'WYLOGOWANIE_BŁĄD', 'Nieprawidłowa metoda HTTP', ip_address)
    return JsonResponse({'error': 'Nieprawidłowa metoda HTTP. Wymagane POST.'}, status=405)




@api_view(['POST'])
@csrf_exempt
def edytuj_profil(request, user_id):
    '''
    Funkcja służąca do edycji danych użytkownika, zwykł user może zmieniać tylko swoje dane, admin każdego usera.
    Brak możliwości użycia nazwy i maila, jeśli są zajęte
    '''
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [request.session.get('user_id')])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    if request.method == 'POST':
        data = json.loads(request.body)
        logged_in_user = request.user.user_id
        nazwa = data.get('nazwa')
        nowy_email = data.get('email')

        # Walidacja danych wejściowych
        if not nazwa or not nowy_email:
            return JsonResponse({'error': 'Nazwa użytkownika i email są wymagane.'}, status=400)
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', nazwa):
            return JsonResponse(
                {'error': 'Nazwa użytkownika może zawierać tylko litery, cyfry i podkreślenia (3-30 znaków).'},
                status=400)
        try:
            validate_email(nowy_email)
        except ValidationError:
            return JsonResponse({'error': 'Nieprawidłowy format adresu email.'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [logged_in_user])
                result = cursor.fetchone()

                if not result:
                    zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', 'Zalogowany użytkownik nie istnieje', ip_address)
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]

            if not is_admin and str(logged_in_user) != str(user_id):
                # Zapis loga o braku uprawnień
                zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', 'Brak uprawnień do edytowania profilu', ip_address)
                return JsonResponse({'error': 'Brak uprawnień do edytowania tego profilu.'}, status=403)

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE nazwa = %s AND user_id != %s", [nazwa, user_id]
                )
                if cursor.fetchone()[0] > 0:
                    zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', 'Nazwa użytkownika jest już zajęta', ip_address)
                    return JsonResponse({'error': 'Podana nazwa użytkownika jest już zajęta.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = %s AND user_id != %s", [nowy_email, user_id]
                )
                if cursor.fetchone()[0] > 0:
                    zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', 'Adres email jest już zajęty', ip_address)
                    return JsonResponse({'error': 'Podany adres email jest już zajęty.'}, status=400)

            with connection.cursor() as cursor:
                sql = "UPDATE users SET nazwa = %s, email = %s WHERE user_id = %s"
                cursor.execute(sql, [nazwa, nowy_email, user_id])

            zapisz_log(email, 'EDYCJA_PROFILU_SUKCES', f'Zaktualizowano profil użytkownika {user_id}', ip_address)
            return JsonResponse({'message': 'Profil został zaktualizowany.'}, status=200)

        except Exception as e:
            zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', f'Błąd podczas aktualizacji: {e}', ip_address)
            return JsonResponse({'error': f'Błąd podczas aktualizacji: {e}'}, status=500)

    zapisz_log(email, 'EDYCJA_PROFILU_BŁĄD', 'Nieprawidłowa metoda HTTP', ip_address)
    return JsonResponse({'error': 'Nieprawidłowa metoda HTTP. Wymagane POST.'}, status=405)


@api_view(['GET'])
def get_ad_details(request, ad_id):
    try:
        # Validate ad_id
        if not isinstance(ad_id, int) and not ad_id.isdigit():
            return JsonResponse({'error': 'Invalid ad ID format'}, status=400)

        ad_id = int(ad_id)

        with connection.cursor() as cursor:
            # Pobierz podstawowe informacje o ogłoszeniu
            cursor.execute("""
                SELECT a.ad_id, a.tytul, a.opis, a.cena, a.status, 
                       a.kategoria_id, c.nazwa as kategoria_nazwa,  -- Zmienione z c.kategoria_nazwa na c.name
                       a.uzytkownik_id, u.nazwa as autor,
                       a.likes_count, a.comments_count,
                       a.data_utworzenia
                FROM ads a
                JOIN categories c ON a.kategoria_id = c.category_id
                JOIN users u ON a.uzytkownik_id = u.user_id
                WHERE a.ad_id = %s AND a.status = True
            """, [ad_id])

            columns = [col[0] for col in cursor.description]
            ad_result = cursor.fetchone()

            if not ad_result:
                return JsonResponse({'error': 'Ogłoszenie nie istnieje'}, status=404)

            ad_data = dict(zip(columns, ad_result))

            # Pobierz komentarze dla ogłoszenia
            cursor.execute("""
                SELECT c.id as comment_id, 
                       c.content as tresc, 
                       c.created_at as data_dodania,
                       u.nazwa as autor,
                       u.user_id as autor_id
                FROM comments c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.ad_id = %s AND c.target_type = 'ad'
                ORDER BY c.created_at DESC
            """, [ad_id])

            columns = [col[0] for col in cursor.description]
            comments = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Przygotuj pełną odpowiedź
            response_data = {
                'ad': {
                    'id': ad_data['ad_id'],
                    'title': ad_data['tytul'],
                    'description': ad_data['opis'],
                    'price': float(ad_data['cena']) if ad_data['cena'] is not None else 0.0,
                    'category': ad_data['kategoria_nazwa'],
                    'category_id': ad_data['kategoria_id'],
                    'author': ad_data['autor'],
                    'author_id': ad_data['uzytkownik_id'],
                    'likes_count': ad_data['likes_count'] or 0,
                    'comments_count': ad_data['comments_count'] or 0,
                    'created_at': ad_data['data_utworzenia'].strftime('%Y-%m-%d') if ad_data[
                        'data_utworzenia'] else None
                },
                'comments': [{
                    'id': comment['comment_id'],
                    'content': comment['tresc'],
                    'created_at': comment['data_dodania'].strftime('%Y-%m-%d %H:%M:%S'),
                    'author': comment['autor'],
                    'author_id': comment['autor_id']
                } for comment in comments]
            }
            print(response_data)
            return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@api_view(['POST'])
@csrf_exempt
def dodaj_ogloszenie(request):
    ip_address = request.META.get('REMOTE_ADDR', '')

    if request.method == 'POST':
        tytul = request.data.get('tytul')
        opis = request.data.get('opis')
        cena = request.data.get('cena')
        kategoria_id = request.data.get('kategoria_id')
        email = request.data.get('email')
        user_id = request.user.user_id
        data_utworzenia = datetime.now()

        print(request.data.get('tytul'))
        print(request.data.get('opis'))
        print(request.data.get('cena'))
        print(request.data.get('kategoria_id'))
        # Walidacja danych wejściowych
        if not tytul or not opis or not cena or not kategoria_id:
            return JsonResponse({'error': 'Wszystkie pola są wymagane.'}, status=400)
        if len(tytul) > 100:
            return JsonResponse({'error': 'Tytuł ogłoszenia nie może przekraczać 100 znaków.'}, status=400)
        if not re.match(r'^[0-9]+(\.[0-9]{1,2})?$', str(cena)):
            return JsonResponse({'error': 'Cena musi być liczbą dodatnią z maksymalnie dwiema cyframi po przecinku.'},
                                status=400)

        sql = """
        INSERT INTO ads (tytul, opis, cena, kategoria_id, uzytkownik_id, status, data_utworzenia)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            with transaction.atomic():  # Rozpoczynamy transakcję
                with connection.cursor() as cursor:
                    cursor.execute(sql, [tytul, opis, cena, kategoria_id, user_id, True, data_utworzenia])

                # Zapis loga o udanym dodaniu ogłoszenia
                zapisz_log(email, 'DODANIE_OGLOSZENIA_SUKCES', f'Dodano ogłoszenie: {tytul}', ip_address)

            return JsonResponse({'message': 'Ogłoszenie zostało dodane.'}, status=201)

        except Exception as e:
            # Zapis loga o błędzie dodania ogłoszenia
            zapisz_log(email, 'DODANIE_OGLOSZENIA_BŁĄD', f'Błąd dodania ogłoszenia: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)



def usun_ogloszenie(request, ad_id):
    '''
    Funkcja usuwania ogłoszeń, user może usuwać tylko swoje ogłoszenia. Admin może usuwać wszystkie ogłoszenia.
    Przed usunięciem ogłoszenia usuwane są powiązane like oraz komentarze.
    '''
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    user_id = request.session.get('user_id')

    # Próba pobrania emaila zalogowanego użytkownika
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    if not user_id:
        # Zapis loga o próbie usunięcia bez logowania
        zapisz_log('', 'USUWANIE_OGLOSZENIA_BŁĄD', 'Próba usunięcia ogłoszenia bez logowania', ip_address)
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    try:
        with transaction.atomic():  # Rozpoczynamy transakcję
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
                result = cursor.fetchone()

                if not result:
                    # Zapis loga o nieistniejącym użytkowniku
                    zapisz_log(email, 'USUWANIE_OGLOSZENIA_BŁĄD', 'Zalogowany użytkownik nie istnieje', ip_address)
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]

                cursor.execute("SELECT uzytkownik_id, tytul FROM ads WHERE ad_id = %s", [ad_id])
                ad_info = cursor.fetchone()

                if not ad_info:
                    # Zapis loga o nieistniejącym ogłoszeniu
                    zapisz_log(email, 'USUWANIE_OGLOSZENIA_BŁĄD', 'Ogłoszenie nie istnieje', ip_address)
                    return JsonResponse({'error': 'Ogłoszenie nie istnieje.'}, status=404)

                ad_owner, ad_tytul = ad_info

                if ad_owner != user_id and not is_admin:
                    # Zapis loga o braku uprawnień
                    zapisz_log(email, 'USUWANIE_OGLOSZENIA_BŁĄD', 'Brak uprawnień do usunięcia ogłoszenia', ip_address)
                    return JsonResponse({'error': 'Brak uprawnień do usunięcia tego ogłoszenia.'}, status=403)

                # Usunięcie powiązanych polubień i komentarzy
                cursor.execute("DELETE FROM likes WHERE ad_id = %s", [ad_id])
                cursor.execute("DELETE FROM comments WHERE ad_id = %s", [ad_id])

                # Usunięcie ogłoszenia
                cursor.execute("DELETE FROM ads WHERE ad_id = %s", [ad_id])

        # Zapis loga o udanym usunięciu ogłoszenia
        zapisz_log(email, 'USUWANIE_OGLOSZENIA_SUKCES', f'Usunięto ogłoszenie: {ad_tytul}', ip_address)
        return JsonResponse({'message': 'Ogłoszenie zostało usunięte.'}, status=200)

    except Exception as e:
        # Zapis loga o błędzie usuwania
        zapisz_log(email, 'USUWANIE_OGLOSZENIA_BŁĄD', f'Błąd usuwania ogłoszenia: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)


def usun_ogloszenie_test(request, ad_id):
    return render(request, 'delete_ad.html', {'ad_id': ad_id})


def edytuj_ogloszenie(request, ad_id):
    '''
    User może edytować tylko swoje ogłoszenia. Admin może edytować każde ogłoszenie.
    '''
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

        try:
            tytul = validate_string(request.POST.get('tytul'), 'Tytuł')
            opis = validate_string(request.POST.get('opis'), 'Opis', max_length=1000)
            cena = validate_positive_float(request.POST.get('cena'), 'Cena')
            kategoria_id = validate_integer(request.POST.get('kategoria_id'), 'Kategoria ID')
            status = request.POST.get('status') == 'true'

            ad_id = validate_integer(ad_id, 'ID ogłoszenia')

            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Pobranie informacji o użytkowniku
                    cursor.execute("SELECT is_staff, email FROM users WHERE user_id = %s", [user_id])
                    result = cursor.fetchone()

                    if not result:
                        return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                    is_admin = result[0]
                    email = result[1]

                    # Pobranie właściciela ogłoszenia
                    cursor.execute("SELECT uzytkownik_id FROM ads WHERE ad_id = %s", [ad_id])
                    ad_owner = cursor.fetchone()

                    if not ad_owner:
                        return JsonResponse({'error': 'Ogłoszenie nie istnieje.'}, status=404)

                    # Sprawdzenie uprawnień do edycji ogłoszenia
                    if ad_owner[0] != user_id and not is_admin:
                        return JsonResponse({'error': 'Brak uprawnień do edytowania tego ogłoszenia.'}, status=403)

                    # Aktualizacja ogłoszenia
                    sql = """
                    UPDATE ads SET tytul = %s, opis = %s, cena = %s, kategoria_id = %s, status = %s
                    WHERE ad_id = %s
                    """
                    cursor.execute(sql, [tytul, opis, cena, kategoria_id, status, ad_id])

                # Zapis loga o edytowaniu ogłoszenia
                ip_address = request.META.get('REMOTE_ADDR', '')
                zapisz_log(email, 'EDYCJA_OGŁOSZENIA', f'Zaktualizowano ogłoszenie ID: {ad_id}', ip_address)

            return JsonResponse({'message': 'Ogłoszenie zostało zaktualizowane.'}, status=200)

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            ip_address = request.META.get('REMOTE_ADDR', '')
            zapisz_log(email, 'EDYCJA_OGŁOSZENIA_BŁĄD', f'Błąd edytowania ogłoszenia ID: {ad_id}, {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)



def edytuj_ogloszenie_test(request, ad_id):
    return render(request, 'edit_ad.html', {'ad_id': ad_id})

@api_view(['GET'])
def przegladaj_ogloszenia(request):
    try:
        category_id = request.GET.get('category')  # Changed from request.data to request.GET
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        sql = "SELECT * FROM ads WHERE status = True"  # Wybór aktywnych ogłoszeń

        # Dodaj filtr po kategorii, jeśli jest podana
        if category_id:
            category_id = validate_integer(category_id, 'Kategoria ID')
            sql += f" AND kategoria_id = {category_id}"

        # Dodaj filtr po minimalnej cenie, jeśli jest podana
        if min_price:
            min_price = validate_positive_float(min_price, 'Minimalna cena')
            sql += f" AND cena >= {min_price}"

        # Dodaj filtr po maksymalnej cenie, jeśli jest podana
        if max_price:
            max_price = validate_positive_float(max_price, 'Maksymalna cena')
            sql += f" AND cena <= {max_price}"

        # Uruchamiamy zapytanie SQL
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            ads = [dict(zip(columns, ad)) for ad in cursor.fetchall()]

        # Zwracamy odpowiedź w formacie JSON
        return JsonResponse({
            'ads': ads
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# def przegladaj_ogloszenia_test(request):
#     '''
#     Funkcja do testowania przegladanie i filtorania ogloszńe, ogloszenia sa zwracane jako JSON
#     '''
#     return render(request, 'display_ads.html')


def przegladaj_ogloszenia_test(request):
    '''
    Funkcja do testowania przegladanie i filtorania ogloszńe, ogloszenia sa zwracane są na stornie (bardziej czytelne)
    '''
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    sql = "SELECT * FROM ads WHERE status = True"

    if category_id:
        sql += f" AND kategoria_id = {category_id}"

    if min_price:
        sql += f" AND cena >= {min_price}"
    if max_price:
        sql += f" AND cena <= {max_price}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            ads = [dict(zip(columns, ad)) for ad in cursor.fetchall()]

        return render(request, 'display_ads.html', {'ads': ads})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@api_view(['POST'])
def dodaj_komentarz(request):
    """
        Funkcja dodawania komentarzy z użyciem raw SQL.
        Obsługuje zarówno komentarze do ogłoszeń, jak i do profili użytkowników.
    """
    ip_address = request.META.get('REMOTE_ADDR', '')
    typ = request.data.get('type')  # 'ad' lub 'user'
    element_id = request.data.get('id')  # ID ogłoszenia lub użytkownika
    tresc = request.data.get('content')  # Treść komentarza
    user_id = request.user.user_id  # ID zalogowanego użytkownika

    # Walidacja danych wejściowych
    if not typ or typ not in ['ad', 'user']:
        return JsonResponse({'error': 'Pole "type" musi być ustawione na "ad" lub "user".'}, status=400)
    if not element_id:
        return JsonResponse({'error': 'Pole "id" jest wymagane.'}, status=400)
    if not tresc or tresc.strip() == '':
        return JsonResponse({'error': 'Treść komentarza nie może być pusta.'}, status=400)

    try:
        # Rozpoczynamy transakcję
        with transaction.atomic():
            with connection.cursor() as cursor:
                if typ == 'ad':
                    # Dodanie komentarza do ogłoszenia
                    sql = """
                        INSERT INTO comments (content, user_id, target_type, ad_id, created_at)
                        VALUES (%s, %s, 'ad', %s, CURRENT_TIMESTAMP)
                    """
                    cursor.execute(sql, [tresc, user_id, element_id])

                    # Aktualizacja licznika komentarzy w tabeli ads
                    cursor.execute(
                        "UPDATE ads SET comments_count = comments_count + 1 WHERE ad_id = %s",
                        [element_id]
                    )

                elif typ == 'user':
                    # Dodanie komentarza do profilu użytkownika
                    sql = """
                        INSERT INTO comments (content, user_id, target_type, target_user_id, created_at)
                        VALUES (%s, %s, 'user', %s, CURRENT_TIMESTAMP)
                    """
                    cursor.execute(sql, [tresc, user_id, element_id])

                    # Aktualizacja licznika komentarzy w tabeli users
                    cursor.execute(
                        "UPDATE users SET comments_received_count = comments_received_count + 1 WHERE user_id = %s",
                        [element_id]
                    )

        # Jeśli wszystko się powiedzie, zwracamy sukces
        return JsonResponse({'message': 'Komentarz został dodany.'}, status=200)

    except Exception as e:
        # W przypadku błędu transakcja zostanie wycofana
        return JsonResponse({'error': str(e)}, status=500)




def dodaj_komentarz_test(request):
    return render(request, 'add_comment.html' )


def edytuj_komentarz(request, comment_id):
    '''
    User moze edytowac tylko swoje komentarze. Admin moze edytowac każdy komentarz. Treść nie może być pusta.
    '''
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

        tresc = request.POST.get('content')

        if not tresc or tresc.strip() == '':
            return JsonResponse({'error': 'Treść komentarza nie może być pusta.'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff, email FROM users WHERE user_id = %s", [user_id])
                result = cursor.fetchone()

                if not result:
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]
                email = result[1]

                # Sprawdzamy, do kogo należy komentarz i jego typ
                cursor.execute("""
                    SELECT user_id 
                    FROM comments 
                    WHERE id = %s
                """, [comment_id])
                comment_owner = cursor.fetchone()


                if not comment_owner:
                    return JsonResponse({'error': 'Komentarz nie istnieje.'}, status=404)

                if comment_owner[0] != user_id:
                    return JsonResponse({'error': 'Brak uprawnień do edytowania tego komentarza.'}, status=403)

                sql = """
                UPDATE comments 
                SET content = %s, created_at = CURRENT_TIMESTAMP 
                WHERE id = %s
                """
                cursor.execute(sql, [tresc, comment_id])


            # Zapis loga o edytowaniu komentarza
            ip_address = request.META.get('REMOTE_ADDR', '')
            zapisz_log(email, 'EDYCJA_KOMENTARZA', f'Zaktualizowano komentarz ID: {comment_id}', ip_address)

            return JsonResponse({'message': 'Komentarz został zaktualizowany.'}, status=200)
        except Exception as e:
            # Zapis loga o błędzie edytowania komentarza
            zapisz_log(email, 'EDYCJA_KOMENTARZA_BŁĄD', f'Błąd edytowania komentarza ID: {comment_id}, {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)



def edytuj_komentarz_test(request, comment_id):
    return render(request, 'edit_comment.html', {'comment_id': comment_id})


def usun_komentarz(request, comment_id):
    '''
    User może usuwać tylko swoje komentarze. Admin może usunąć każdy komentarz.
    '''
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff, email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]
            email = result[1]

            cursor.execute("""
                SELECT * 
                FROM comments 
                WHERE id = %s
            """, [comment_id])
            comment_owner = cursor.fetchone()
            print(comment_owner)

            if not comment_owner:
                return JsonResponse({'error': 'Komentarz nie istnieje.'}, status=404)

            if comment_owner[3] != user_id:  # Sprawdzenie właściciela komentarza
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego komentarza.'}, status=403)


            #SPRAWDZENEI CZY JEST ADMINEM

            # Sprawdzanie typu komentarza
            if comment_owner[4] == 'ad':
                element_id = comment_owner[5]  # ad_id
                cursor.execute(
                    "UPDATE ads SET comments_count = comments_count - 1 WHERE ad_id = %s",
                    [element_id])

            elif comment_owner[4] == 'user':
                element_id = comment_owner[6]  # target_user_id
                cursor.execute(
                    "UPDATE users SET comments_received_count = comments_received_count - 1 WHERE user_id = %s",
                    [element_id])

            # Usuwanie komentarza
            cursor.execute("DELETE FROM comments WHERE id = %s", [comment_id])

            # Zapis loga o usunięciu komentarza
            ip_address = request.META.get('REMOTE_ADDR', '')
            zapisz_log(email, 'USUNIĘCIE_KOMENTARZA', f'Usunięto komentarz ID: {comment_id}', ip_address)

        return JsonResponse({'message': 'Komentarz został usunięty.'}, status=200)

    except Exception as e:
        # Zapis loga o błędzie usunięcia komentarza
        zapisz_log(email, 'USUNIĘCIE_KOMENTARZA_BŁĄD', f'Błąd usunięcia komentarza ID: {comment_id}, {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)




def usun_komentarz_test(request, comment_id):
    return render(request, 'delete_comment.html', {'comment_id': comment_id})


def polub(request):
    """
    Funkcja dodawania polubień dla ogłoszeń i profili użytkowników.
    Obsługuje zabezpieczenie przed wielokrotnym polubieniem tego samego elementu.
    """
    user_id = request.request.user_id
    ip_address = request.META.get('REMOTE_ADDR', '')

    if not user_id:
        zapisz_log('Brak_email', 'POLUBIENIE_BŁĄD', 'Brak zalogowanego użytkownika', ip_address)
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    email = ''
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        zapisz_log(email, 'POLUBIENIE_BŁĄD', f'Błąd pobierania emaila: {e}', ip_address)

    typ = request.POST.get('type')
    element_id = request.POST.get('id')

    if not typ or typ not in ['ad', 'user']:
        zapisz_log(email, 'POLUBIENIE_BŁĄD', 'Nieprawidłowy typ polubienia', ip_address)
        return JsonResponse({'error': 'Pole "type" musi być ustawione na "ad" lub "user".'}, status=400)

    if not element_id:
        zapisz_log(email, 'POLUBIENIE_BŁĄD', 'Brak elementu do polubienia', ip_address)
        return JsonResponse({'error': 'Pole "id" jest wymagane.'}, status=400)

    if typ == 'ad':
        sql_check = """
            SELECT COUNT(*) FROM likes 
            WHERE target_type = 'ad' 
            AND ad_id = %s 
            AND user_id = %s
        """
        sql_insert = """
            INSERT INTO likes (user_id, target_type, ad_id)
            VALUES (%s, 'ad', %s)
        """
        params = [element_id, user_id]
        update_likes_count = "UPDATE ads SET likes_count = likes_count + 1 WHERE ad_id = %s"
    elif typ == 'user':
        sql_check = """
            SELECT COUNT(*) FROM likes 
            WHERE target_type = 'user' 
            AND target_user_id = %s 
            AND user_id = %s
        """
        sql_insert = """
            INSERT INTO likes (user_id, target_type, target_user_id)
            VALUES (%s, 'user', %s)
        """
        params = [element_id, user_id]
        update_likes_count = "UPDATE users SET likes_received_count = likes_received_count + 1 WHERE user_id = %s"

    try:
        with transaction.atomic():  # Rozpoczynamy transakcję
            with connection.cursor() as cursor:
                # Sprawdzenie, czy polubienie już istnieje
                cursor.execute(sql_check, params)
                result = cursor.fetchone()

                if result[0] == 0:
                    # Dodanie polubienia
                    cursor.execute(sql_insert, [user_id, element_id])

                    # Aktualizacja licznika polubień
                    cursor.execute(update_likes_count, [element_id])

                    zapisz_log(email, 'POLUBIENIE_SUKCES',
                               f'Polubiono {"ogłoszenie" if typ == "ad" else "profil"} {element_id}', ip_address)
                    return JsonResponse({'message': f'Dodano polubienie {"ogłoszenia" if typ == "ad" else "profilu"}'},
                                        status=200)
                else:
                    zapisz_log(email, 'POLUBIENIE_BŁĄD',
                               f'Polubienie {"ogłoszenia" if typ == "ad" else "profilu"} już istnieje.', ip_address)
                    return JsonResponse(
                        {'message': f'Polubienie {"ogłoszenia" if typ == "ad" else "profilu"} już istnieje.'},
                        status=400)

    except Exception as e:
        zapisz_log(email, 'POLUBIENIE_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)



def polub_test(request):
    return render(request, 'like_ad.html')

def usun_polubienie(request, like_id):
    '''
    User może usuwać tylko swoje polubienia. Admin może usunąć każde polubienie.
    '''
    user_id = request.request.user_id
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    if not user_id:
        zapisz_log('Brak_email', 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Brak zalogowanego użytkownika', ip_address)
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]

            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Zalogowany użytkownik nie istnieje', ip_address)
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            cursor.execute("""
                SELECT user_id, target_type, ad_id, target_user_id 
                FROM likes 
                WHERE id = %s
            """, [like_id])
            like_data = cursor.fetchone()

            if not like_data:
                zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Like nie istnieje', ip_address)
                return JsonResponse({'error': 'Like nie istnieje.'}, status=404)

            # Sprawdzamy, czy użytkownik ma prawo usunąć to polubienie
            if like_data[0] != user_id and not is_admin:
                zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Brak uprawnień do usunięcia tego like.', ip_address)
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego like.'}, status=403)

            # Usuwamy polubienie
            cursor.execute("DELETE FROM likes WHERE id = %s", [like_id])

            # Aktualizujemy liczniki
            if like_data[1] == 'ad':  # Polubienie ogłoszenia
                cursor.execute("UPDATE ads SET likes_count = likes_count - 1 WHERE ad_id = %s", [like_data[2]])
            elif like_data[1] == 'user':  # Polubienie użytkownika
                cursor.execute("UPDATE users SET likes_received_count = likes_received_count - 1 WHERE user_id = %s", [like_data[3]])

        zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_SUKCES', f'Usunięto polubienie {like_id}', ip_address)
        return JsonResponse({'message': 'Likes został usunięty.'}, status=200)

    except Exception as e:
        zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)



def usun_polubienie_test(request, like_id):
    return render(request, 'dislike_ad.html', {'like_id': like_id})



def ocen_uzytkownika(request, oceniany_id):
    ocena = request.POST.get('ocena')
    oceniajacy_id = request.session.get('user_id')
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    if not oceniajacy_id:
        zapisz_log('Brak_email', 'OCENA_BŁĄD', 'Brak zalogowanego użytkownika', ip_address)
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    try:
        with transaction.atomic():  # Rozpoczyna transakcję
            with connection.cursor() as cursor:
                # Sprawdzamy email oceniajacego
                cursor.execute("SELECT email FROM users WHERE user_id = %s", [oceniajacy_id])
                result = cursor.fetchone()
                if result:
                    email = result[0]

                # Sprawdzamy, czy użytkownik już ocenił ocenianego użytkownika
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ratings 
                    WHERE oceniajacy_id = %s AND oceniany_id = %s
                """, [oceniajacy_id, oceniany_id])

                count_result = cursor.fetchone()
                if count_result and count_result[0] > 0:
                    zapisz_log(email, 'OCENA_BŁĄD', f'Użytkownik {oceniajacy_id} próbował ponownie ocenić użytkownika {oceniany_id}', ip_address)
                    return JsonResponse({'error': 'Użytkownik może dodać tylko jedną ocenę dla tego samego użytkownika.'}, status=400)

                # Dodajemy ocenę do tabeli ratings
                sql_insert = """
                    INSERT INTO ratings (oceniajacy_id, oceniany_id, ocena, data_oceny)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                """
                cursor.execute(sql_insert, [oceniajacy_id, oceniany_id, ocena])

                # Obliczamy średnią ocenę użytkownika
                cursor.execute("""
                    SELECT AVG(ocena) 
                    FROM ratings 
                    WHERE oceniany_id = %s
                """, [oceniany_id])

                result = cursor.fetchone()
                if result and result[0] is not None:
                    average_rating = result[0]
                else:
                    average_rating = 0

                # Aktualizujemy kolumnę average_rating w tabeli users
                cursor.execute("""
                    UPDATE users 
                    SET average_rating = %s 
                    WHERE user_id = %s
                """, [average_rating, oceniany_id])

        zapisz_log(email, 'OCENA_SUKCES', f'Oceniono użytkownika {oceniany_id} na {ocena}', ip_address)
        return JsonResponse({'message': 'Oceniono użytkownika.', 'average_rating': average_rating}, status=200)

    except Exception as e:
        # W przypadku błędu transakcja zostanie automatycznie wycofana
        zapisz_log(email, 'OCENA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)



def ocen_uzytkownika_test(request, oceniany_id):
    return render(request, 'rate_user.html', {'oceniany_id': oceniany_id})

@admin_required
def dezaktywuj_uzytkownika(request, user_id):
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''
    oceniajacy_id = request.session.get('user_id')

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [oceniajacy_id])
            result = cursor.fetchone()
            if result:
                email = result[0]

            sql = "UPDATE users SET is_active = 0 WHERE user_id = %s"
            cursor.execute(sql, [user_id])

        zapisz_log(email, 'DEZAKTYWACJA_UŻYTKOWNIKA_SUKCES', f'Dezaktywowany użytkownik {user_id}', ip_address)
        return JsonResponse({'message': 'Użytkownik został dezaktywowany'}, status=200)

    except Exception as e:
        zapisz_log(email, 'DEZAKTYWACJA_UŻYTKOWNIKA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)

def dezaktywuj_uzytkownika_test(request, user_id):
    return render(request, 'admin/deactivate_user.html', {'user_id': user_id})


@admin_required
def aktywuj_uzytkownika(request, user_id):
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''
    oceniajacy_id = request.session.get('user_id')

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [oceniajacy_id])
            result = cursor.fetchone()
            if result:
                email = result[0]

            sql = "UPDATE users SET is_active = 1 WHERE user_id = %s"
            cursor.execute(sql, [user_id])

        zapisz_log(email, 'AKTYWACJA_UŻYTKOWNIKA_SUKCES', f'Aktywowano użytkownika {user_id}', ip_address)
        return JsonResponse({'message': 'Użytkownik został aktywowany', 'status': 'success'}, status=200)

    except Exception as e:
        zapisz_log(email, 'AKTYWACJA_UŻYTKOWNIKA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def pobierz_kategorie(request):
    """
    Pobiera listę wszystkich kategorii z bazy danych.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT category_id, nazwa FROM categories")
            categories = [
                {
                    'id': row[0],
                    'name': row[1]
                } for row in cursor.fetchall()
            ]

        return JsonResponse(categories, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
def stworz_kategorie(request):
    user_id = request.session.get('user_id')
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    try:
        if request.method == 'POST':
            nazwa = request.POST.get('nazwa')

            if not nazwa or nazwa.strip() == '':
                zapisz_log(email, 'STWORZ_KATEGORIE_BŁĄD', 'Nazwa kategorii nie może być pusta', ip_address)
                return JsonResponse({'error': 'Nazwa kategorii nie może być pusta.'}, status=400)

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM categories WHERE nazwa = %s", [nazwa])
                    category_exists = cursor.fetchone()[0] > 0

                    if category_exists:
                        zapisz_log(email, 'STWORZ_KATEGORIE_BŁĄD', 'Kategoria o podanej nazwie już istnieje', ip_address)
                        return JsonResponse({'error': 'Kategoria o podanej nazwie już istnieje.'}, status=400)

                    sql = "INSERT INTO categories (nazwa) VALUES (%s)"
                    cursor.execute(sql, [nazwa])

                zapisz_log(email, 'STWORZ_KATEGORIE_SUKCES', f'Utworzono kategorię: {nazwa}', ip_address)
                return JsonResponse({'message': 'Kategoria została pomyślnie utworzona.'}, status=200)
            except Exception as e:
                zapisz_log(email, 'STWORZ_KATEGORIE_BŁĄD', f'Błąd podczas tworzenia kategorii: {e}', ip_address)
                return JsonResponse({'error': str(e)}, status=400)

        zapisz_log(email, 'STWORZ_KATEGORIE_BŁĄD', 'Nieprawidłowa metoda HTTP', ip_address)
        return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        zapisz_log(email, 'STWORZ_KATEGORIE_BŁĄD', f'Nieoczekiwany błąd: {e}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)


def stworz_kategorie_test(request):
    return render(request, 'admin/add_category.html')

@admin_required
def edytuj_kategorie(request, category_id):
    user_id = request.session.get('user_id')
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', 'Zalogowany użytkownik nie istnieje', ip_address)
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            if not is_admin:
                zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', 'Brak uprawnień do edytowania kategorii', ip_address)
                return JsonResponse({'error': 'Brak uprawnień do edytowania kategorii.'}, status=403)

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM categories WHERE category_id = %s", [category_id])
            category_exists = cursor.fetchone()[0] > 0

            if not category_exists:
                zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', 'Kategoria o podanym ID nie istnieje', ip_address)
                return JsonResponse({'error': 'Kategoria o podanym ID nie istnieje.'}, status=404)

        if request.method == 'POST':
            nowa_nazwa = request.POST.get('nazwa')

            if not nowa_nazwa or nowa_nazwa.strip() == '':
                zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', 'Nazwa kategorii nie może być pusta', ip_address)
                return JsonResponse({'error': 'Nazwa kategorii nie może być pusta.'}, status=400)

            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE categories SET nazwa = %s WHERE category_id = %s", [nowa_nazwa, category_id])

                zapisz_log(email, 'EDYTUJ_KATEGORIE_SUKCES', f'Zaktualizowano kategorię ID: {category_id} na nazwę: {nowa_nazwa}', ip_address)
                return JsonResponse({'message': 'Kategoria została zaktualizowana.'}, status=200)

            except Exception as e:
                zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', f'Błąd podczas edycji kategorii: {e}', ip_address)
                return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        zapisz_log(email, 'EDYTUJ_KATEGORIE_BŁĄD', f'Nieoczekiwany błąd: {e}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)

def edytuj_kategorie_test(request, category_id):
    return render(request, 'admin/edit_category.html', {'category_id': category_id})

@admin_required
def usun_kategorie(request, category_id):
    user_id = request.session.get('user_id')
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                zapisz_log(email, 'USUN_KATEGORIE_BŁĄD', 'Zalogowany użytkownik nie istnieje', ip_address)
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            if not is_admin:
                zapisz_log(email, 'USUN_KATEGORIE_BŁĄD', 'Brak uprawnień do usuwania kategorii', ip_address)
                return JsonResponse({'error': 'Brak uprawnień do usuwania kategorii.'}, status=403)

        if request.method == 'POST':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM categories WHERE category_id = %s", [category_id])

                zapisz_log(email, 'USUN_KATEGORIE_SUKCES', f'Usunięto kategorię ID: {category_id}', ip_address)
                return JsonResponse({'message': 'Kategoria została usunięta.'}, status=200)

            except Exception as e:
                zapisz_log(email, 'USUN_KATEGORIE_BŁĄD', f'Błąd podczas usuwania kategorii: {e}', ip_address)
                return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        zapisz_log(email, 'USUN_KATEGORIE_BŁĄD', f'Nieoczekiwany błąd: {e}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)



def usun_kategorie_test(request, category_id):
    return render(request, 'admin/delete_category.html', {'category_id': category_id})

@admin_required
def pokaz_logi(request):
    '''
    Funkcja wyświetlania logów dla staff'u, test
    '''
    sql = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            logs = cursor.fetchall()

        return JsonResponse({'logs': logs }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def zapisz_log(email, action, details, ip_address):
    '''
    Funkcja do zapisu logów w bazie danych
    '''
    sql = """
    INSERT INTO logs (user_email, action, details, ip_address)
    VALUES (%s, %s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [email, action, details, ip_address])
    except Exception as e:
        # W razie niepowodzenia zapisu loga, wydrukuj błąd
        print(f"Błąd zapisu loga: {e}")