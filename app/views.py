from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from datetime import datetime

from .decorators import admin_required
from django.contrib.auth.decorators import login_required


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


def zarejestruj_uzytkownika(request):
    '''
    Funkcja rejestracji użytkownika ze sprawdzeniem czy podany mail nie jest już wykorzystany
    '''
    if request.method == 'POST':
        nazwa = request.POST.get('nazwa')
        email = request.POST.get('email')
        haslo = request.POST.get('haslo')
        data_utworzenia = datetime.now()
        ip_address = request.META.get('REMOTE_ADDR', '')

        # Zapis loga o próbie rejestracji
        zapisz_log(email, 'REJESTRACJA_PRÓBA', f'Próba rejestracji użytkownika {nazwa}', ip_address)

        check_email_sql = "SELECT COUNT(*) FROM users WHERE email = %s"
        insert_sql = """
        INSERT INTO users (nazwa, email, haslo, data_utworzenia)
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


def zaloguj_uzytkownika(request):
    '''
    Funkcja logowania użytkownika
    '''
    if request.method == 'POST':
        email = request.POST.get('email')
        haslo = request.POST.get('haslo')
        ip_address = request.META.get('REMOTE_ADDR', '')

        # Zapis loga o próbie logowania
        zapisz_log(email, 'LOGOWANIE_PRÓBA', 'Próba logowania', ip_address)

        sql = "SELECT * FROM users WHERE email = %s AND haslo = %s"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [email, haslo])
                user = cursor.fetchone()

                if user:
                    request.session['user_id'] = user[0]
                    # Zapis loga o udanym logowaniu
                    zapisz_log(email, 'LOGOWANIE_SUKCES', 'Użytkownik zalogowany pomyślnie', ip_address)
                    return JsonResponse({'message': 'Zalogowano pomyślnie.'}, status=200)

            # Zapis loga o nieudanej próbie logowania
            zapisz_log(email, 'LOGOWANIE_BŁĄD', 'Nieprawidłowy email lub hasło', ip_address)
            return JsonResponse({'error': 'Nieprawidłowy email lub hasło.'}, status=400)

        except Exception as e:
            # Zapis loga o błędzie logowania
            zapisz_log(email, 'LOGOWANIE_BŁĄD', f'Błąd logowania: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)



def zaloguj_uzytkownika_test(request):
    return render(request, 'login.html')


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


def wyloguj_uzytkownika_test(request):
    return render(request, 'logout.html')


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
        logged_in_user = request.session.get('user_id')
        nazwa = request.POST.get('nazwa')
        nowy_email = request.POST.get('email')

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


def edytuj_profil_test(request, user_id):
    return render(request, 'edit_profile.html', {'user_id': user_id})


def dodaj_ogloszenie(request):
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = ''

    # Próba pobrania emaila zalogowanego użytkownika
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [request.session.get('user_id')])
            result = cursor.fetchone()
            if result:
                email = result[0]
    except Exception as e:
        print(f"Błąd pobierania emaila: {e}")

    if request.method == 'POST':
        tytul = request.POST.get('tytul')
        opis = request.POST.get('opis')
        cena = request.POST.get('cena')
        kategoria_id = request.POST.get('kategoria_id')
        user_id = request.session.get('user_id')
        data_utworzenia = datetime.now()

        sql = """
        INSERT INTO ads (tytul, opis, cena, kategoria_id, uzytkownik_id, status, data_utworzenia)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [tytul, opis, cena, kategoria_id, user_id, True, data_utworzenia])

            zapisz_log(email, 'DODANIE_OGLOSZENIA_SUKCES', f'Dodano ogłoszenie: {tytul}', ip_address)
            return JsonResponse({'message': 'Ogłoszenie zostało dodane.'}, status=201)
        except Exception as e:
            # Zapis loga o błędzie dodania ogłoszenia
            zapisz_log(email, 'DODANIE_OGLOSZENIA_BŁĄD', f'Błąd dodania ogłoszenia: {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)

def dodaj_ogloszenie_test(request):
    return render(request, 'add_ad.html')


def usun_ogloszenie(request, ad_id):
    '''
    Funkcja usuwania ogłoszeń, user może usuwać tylko swoje ogłoszenia. Admin może usuwać wszystkie ogłoszenia.
    Przed usunięciem ogłoszenia usuwane są powiązane like oraz komentarze
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

            cursor.execute("DELETE FROM likes WHERE ad_id = %s", [ad_id])

            cursor.execute("DELETE FROM comments WHERE ad_id = %s", [ad_id])

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
    User moze edytowac tylko swoje ogloszenia. Admin moze edytkować kazde ogłoszenie.
    '''
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

        tytul = request.POST.get('tytul')
        opis = request.POST.get('opis')
        cena = request.POST.get('cena')
        kategoria_id = request.POST.get('kategoria_id')
        status = request.POST.get('status') == 'true'

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff, email FROM users WHERE user_id = %s", [user_id])
                result = cursor.fetchone()

                if not result:
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]
                email = result[1]

                cursor.execute("SELECT uzytkownik_id FROM ads WHERE ad_id = %s", [ad_id])
                ad_owner = cursor.fetchone()

                if not ad_owner:
                    return JsonResponse({'error': 'Ogłoszenie nie istnieje.'}, status=404)

                if ad_owner[0] != user_id and not is_admin:
                    return JsonResponse({'error': 'Brak uprawnień do edytowania tego ogłoszenia.'}, status=403)

                sql = """
                UPDATE ads SET tytul = %s, opis = %s, cena = %s, kategoria_id = %s, status = %s
                WHERE ad_id = %s
                """
                cursor.execute(sql, [tytul, opis, cena, kategoria_id, status, ad_id])

            # Zapis loga o edytowaniu ogłoszenia
            ip_address = request.META.get('REMOTE_ADDR', '')
            zapisz_log(email, 'EDYCJA_OGŁOSZENIA', f'Zaktualizowano ogłoszenie ID: {ad_id}', ip_address)

            return JsonResponse({'message': 'Ogłoszenie zostało zaktualizowane.'}, status=200)

        except Exception as e:
            # Zapis loga o błędzie edytowania ogłoszenia
            zapisz_log(email, 'EDYCJA_OGŁOSZENIA_BŁĄD', f'Błąd edytowania ogłoszenia ID: {ad_id}, {str(e)}', ip_address)
            return JsonResponse({'error': str(e)}, status=500)


def edytuj_ogloszenie_test(request, ad_id):
    return render(request, 'edit_ad.html', {'ad_id': ad_id})


def przegladaj_ogloszenia(request):
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

        return JsonResponse({'ads': ads}, status=200)
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



def dodaj_komentarz(request):
    """
    Funkcja dodawania komentarzy z użyciem raw SQL.
    Obsługuje zarówno komentarze do ogłoszeń, jak i do profili użytkowników.
    """
    # Pobranie danych z requesta
    typ = request.POST.get('type')  # 'ad' lub 'user'
    element_id = request.POST.get('id')  # ID ogłoszenia lub użytkownika
    tresc = request.POST.get('content')  # Treść komentarza
    uzytkownik_id = request.session.get('user_id')  # ID zalogowanego użytkownika

    # Walidacja danych
    if not typ or typ not in ['ad', 'user']:
        return JsonResponse({'error': 'Pole "type" musi być ustawione na "ad" lub "user".'}, status=400)

    if not element_id:
        return JsonResponse({'error': 'Pole "id" jest wymagane.'}, status=400)

    if not tresc or tresc.strip() == '':
        return JsonResponse({'error': 'Treść komentarza nie może być pusta.'}, status=400)

    try:
        with connection.cursor() as cursor:
            # Pobieranie adresu e-mail użytkownika
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [uzytkownik_id])
            user_email = cursor.fetchone()[0]

            # Przygotowanie SQL w zależności od typu
            if typ == 'ad':
                sql = """
                    INSERT INTO comments (content, user_id, target_type, ad_id, created_at)
                    VALUES (%s, %s, 'ad', %s, CURRENT_TIMESTAMP)
                """
            elif typ == 'user':
                sql = """
                    INSERT INTO comments (content, user_id, target_type, target_user_id, created_at)
                    VALUES (%s, %s, 'user', %s, CURRENT_TIMESTAMP)
                """
            params = [tresc, uzytkownik_id, element_id]

            # Wykonanie zapytania
            cursor.execute(sql, params)

            # Zapis loga o dodaniu komentarza
            ip_address = request.META.get('REMOTE_ADDR', '')
            zapisz_log(user_email, 'DODANIE_KOMENTARZA', f'Dodano komentarz do {typ} ID: {element_id}', ip_address)

        return JsonResponse({'message': 'Komentarz został dodany.'}, status=200)

    except Exception as e:
        # Zapis loga o błędzie dodawania komentarza
        zapisz_log(user_email, 'DODANIE_KOMENTARZA_BŁĄD', f'Błąd dodawania komentarza do {typ} ID: {element_id}, {str(e)}', ip_address)
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

                if comment_owner[0] != user_id and not is_admin:
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
    User moze usuwać tylko swoje komentarze. Admin moze usunąć każdy komentarz.
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
                SELECT user_id 
                FROM comments 
                WHERE id = %s
            """, [comment_id])
            comment_owner = cursor.fetchone()

            if not comment_owner:
                return JsonResponse({'error': 'Komentarz nie istnieje.'}, status=404)

            if comment_owner[0] != user_id and not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego komentarza.'}, status=403)

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
    Funkcja dodawania polubień dla ogłoszeń i profili użytkowników. DODAJ FUNKCJONALNOSC ABY NIE MOZNA BYLO POLUBIC 2 RAZY TEGO SAMEGO AD LBU USER
    """
    user_id = request.session.get('user_id')
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
        params = [user_id, element_id]
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
        params = [user_id, element_id]

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_check, params)
            result = cursor.fetchone()

            if result[0] == 0:
                cursor.execute(sql_insert, params)
                zapisz_log(email, 'POLUBIENIE_SUKCES',
                           f'Polubiono {"ogłoszenie" if typ == "ad" else "profil"} {element_id}', ip_address)
                return JsonResponse({'message': f'Dodano polubienie {"ogłoszenia" if typ == "ad" else "profilu"}'},
                                    status=200)
            else:
                zapisz_log(email, 'POLUBIENIE_BŁĄD',
                           f'Polubienie {"ogłoszenia" if typ == "ad" else "profilu"} już istnieje.', ip_address)
                return JsonResponse(
                    {'message': f'Polubienie {"ogłoszenia" if typ == "ad" else "profilu"} już istnieje.'}, status=400)

    except Exception as e:
        zapisz_log(email, 'POLUBIENIE_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)



def polub_test(request):
    return render(request, 'like_ad.html')

def usun_polubienie(request, like_id):
    '''
    User moze usuwać tylko swoje polubienia. Admin moze usunąć każde polubienie.
    '''
    user_id = request.session.get('user_id')
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
                SELECT user_id 
                FROM likes 
                WHERE id = %s
            """, [like_id])
            comment_owner = cursor.fetchone()

            if not comment_owner:
                zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Like nie istnieje', ip_address)
                return JsonResponse({'error': 'Like nie istnieje.'}, status=404)

            if comment_owner[0] != user_id and not is_admin:
                zapisz_log(email, 'USUNIĘCIE_POLUBIENIA_BŁĄD', 'Brak uprawnień do usunięcia tego like.', ip_address)
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego like.'}, status=403)

            cursor.execute("DELETE FROM likes WHERE id = %s", [like_id])

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

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", [oceniajacy_id])
            result = cursor.fetchone()
            if result:
                email = result[0]

            sql_insert = """
                INSERT INTO ratings (oceniajacy_id, oceniany_id, ocena, data_oceny)
                VALUES (%s, %s, %s, CURRENT_DATE)
            """
            cursor.execute(sql_insert, [oceniajacy_id, oceniany_id, ocena])

        zapisz_log(email, 'OCENA_SUKCES', f'Oceniono użytkownika {oceniany_id} na {ocena}', ip_address)
        return JsonResponse({'message': 'Oceniono użytkownika.'}, status=200)
    except Exception as e:
        zapisz_log(email, 'OCENA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)


def ocen_uzytkownika_test(request, oceniany_id):
    return render(request, 'rate_user.html', {'oceniany_id': oceniany_id})

@admin_required
def dezaktywuj_uzytkownika(request, user_id):
    ip_address = request.META.get('REMOTE_ADDR', '')
    email = request.user.email  # Assuming admin email is in the session or user object

    try:
        with connection.cursor() as cursor:
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
    email = request.user.email  # Assuming admin email is in the session or user object

    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET is_active = 1 WHERE user_id = %s"
            cursor.execute(sql, [user_id])

        zapisz_log(email, 'AKTYWACJA_UŻYTKOWNIKA_SUKCES', f'Aktywowano użytkownika {user_id}', ip_address)
        return JsonResponse({'message': 'Użytkownik został aktywowany', 'status': 'success'}, status=200)

    except Exception as e:
        zapisz_log(email, 'AKTYWACJA_UŻYTKOWNIKA_BŁĄD', f'Błąd: {str(e)}', ip_address)
        return JsonResponse({'error': str(e)}, status=500)


def aktywuj_uzytkownika_test(request, user_id):
    return render(request, 'activate_user.html', {'user_id': user_id})

@admin_required
def stworz_kategorie(request):
    user_id = request.session.get('user_id')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            if not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do tworzenia kategorii.'}, status=403)

        if request.method == 'POST':
            nazwa = request.POST.get('nazwa')

            # Walidacja, aby nazwa nie była pusta
            if not nazwa or nazwa.strip() == '':
                return JsonResponse({'error': 'Nazwa kategorii nie może być pusta.'}, status=400)

            try:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO categories (nazwa) VALUES (%s)"
                    cursor.execute(sql, [nazwa])
                return JsonResponse({'message': 'Kategoria została pomyślnie utworzona.'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        return render(request, 'stworz_kategorie.html')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def stworz_kategorie_test(request):
    return render(request, 'admin/add_category.html')

@admin_required
def edytuj_kategorie(request, category_id):
    user_id = request.session.get('user_id')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            if not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do edytowania kategorii.'}, status=403)

        if request.method == 'POST':
            nowa_nazwa = request.POST.get('nazwa')

            # Walidacja, aby nazwa nie była pusta
            if not nowa_nazwa or nowa_nazwa.strip() == '':
                return JsonResponse({'error': 'Nazwa kategorii nie może być pusta.'}, status=400)

            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE categories SET nazwa = %s WHERE category_id = %s", [nowa_nazwa, category_id])

                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM categories WHERE category_id = %s", [category_id])
                    category = cursor.fetchone()

                if not category:
                    return JsonResponse({'error': 'Kategoria nie istnieje.'}, status=404)

                return JsonResponse({'message': 'Kategoria została zaktualizowana.'}, status=200)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def edytuj_kategorie_test(request, category_id):
    return render(request, 'admin/edit_category.html', {'category_id': category_id})

@admin_required
def usun_kategorie(request, category_id):
    user_id = request.session.get('user_id')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            if not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do usuwania kategorii.'}, status=403)

        if request.method == 'POST':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM categories WHERE category_id = %s", [category_id])

                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM categories WHERE category_id = %s", [category_id])
                    category = cursor.fetchone()



                if category:
                    return JsonResponse({'error': 'Nie udało się usunąć kategorii.'}, status=400)

                return JsonResponse({'message': 'Kategoria została usunięta.'}, status=200)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def usun_kategorie_test(request, category_id):
    return render(request, 'admin/delete_category.html', {'category_id': category_id})

@admin_required
def pokaz_logi(request):
    '''
    Funkcja wyświetlania logów dla staff'u
    '''
    sql = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            logs = cursor.fetchall()

        return JsonResponse({'logs': logs }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


