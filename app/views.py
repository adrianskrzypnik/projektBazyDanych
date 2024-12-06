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


def zarejestruj_uzytkownika(request):
    '''
    Funkcja rejestracji użytkownika ze sprawdzeniem czy podany mail nie jest już wykorzystany
    '''
    if request.method == 'POST':
        nazwa = request.POST.get('nazwa')
        email = request.POST.get('email')
        haslo = request.POST.get('haslo')
        data_utworzenia = datetime.now()

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
                    return JsonResponse(
                        {'error': 'Użytkownik z podanym adresem e-mail już istnieje.'},
                        status=400
                    )

                cursor.execute(insert_sql, [nazwa, email, haslo, data_utworzenia])

            return JsonResponse({'message': 'Użytkownik został zarejestrowany.'}, status=201)
        except Exception as e:
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


        sql = "SELECT * FROM users WHERE email = %s AND haslo = %s"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [email, haslo])
                user = cursor.fetchone()

                if user:
                    request.session['user_id'] = user[0]
                    return JsonResponse({'message': 'Zalogowano pomyślnie.'}, status=200)

            return JsonResponse({'error': 'Nieprawidłowy email lub hasło.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def zaloguj_uzytkownika_test(request):
    return render(request, 'login.html')


def wyloguj_uzytkownika(request):
    '''
    Funkcja wylogowania użytkownika
    '''
    if request.method == 'POST':
        try:
            if 'user_id' in request.session:
                del request.session['user_id']

            request.session.flush()

            return JsonResponse({'message': 'Wylogowano pomyślnie.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Nieprawidłowa metoda HTTP. Wymagane POST.'}, status=405)


def wyloguj_uzytkownika_test(request):
    return render(request, 'logout.html')

def edytuj_profil(request, user_id):
    '''
    Funckja służąca do edycji danych użytkownika, zwykł user może zmieniać tylko swoje dane, admin każdego usera.
    Brak możliwości użycia nazwy i maila, jeśli są zajęte
    '''
    if request.method == 'POST':
        logged_in_user = request.session.get('user_id')  # ID zalogowanego użytkownika
        nazwa = request.POST.get('nazwa')  # Nowa nazwa
        email = request.POST.get('email')  # Nowy email

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [logged_in_user])
                result = cursor.fetchone()

                if not result:
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]

            # Sprawdzenie uprawnień
            if not is_admin and str(logged_in_user) != str(user_id):
                return JsonResponse({'error': 'Brak uprawnień do edytowania tego profilu.'}, status=403)

            # Sprawdzenie, czy nazwa użytkownika jest zajęta
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE nazwa = %s AND user_id != %s", [nazwa, user_id]
                )
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'error': 'Podana nazwa użytkownika jest już zajęta.'}, status=400)

            # Sprawdzenie, czy adres email jest zajęty
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = %s AND user_id != %s", [email, user_id]
                )
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'error': 'Podany adres email jest już zajęty.'}, status=400)

            # Aktualizacja profilu
            with connection.cursor() as cursor:
                sql = "UPDATE users SET nazwa = %s, email = %s WHERE user_id = %s"
                cursor.execute(sql, [nazwa, email, user_id])

            return JsonResponse({'message': 'Profil został zaktualizowany.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Błąd podczas aktualizacji: {e}'}, status=500)

    return JsonResponse({'error': 'Nieprawidłowa metoda HTTP. Wymagane POST.'}, status=405)






def edytuj_profil_test(request, user_id):
    return render(request, 'edit_profile.html', {'user_id': user_id})

def dodaj_ogloszenie(request):
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

            return JsonResponse({'message': 'Ogłoszenie zostało dodane.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def dodaj_ogloszenie_test(request):
    return render(request, 'add_ad.html')


def usun_ogloszenie(request, ad_id):
    '''
    Funkcja usuwania ogłoszeń, user może usuwać tylko swoje ogłoszenia. Admin może usuwać wszystkie ogłoszenia.
    Przed usunięciem ogłoszenia usuwane są powiązane like oraz komentarze
    '''
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]

            cursor.execute("SELECT uzytkownik_id FROM ads WHERE ad_id = %s", [ad_id])
            ad_owner = cursor.fetchone()

            if not ad_owner:
                return JsonResponse({'error': 'Ogłoszenie nie istnieje.'}, status=404)

            if ad_owner[0] != user_id and not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego ogłoszenia.'}, status=403)

            cursor.execute("DELETE FROM likes WHERE ogloszenie_id = %s", [ad_id])

            cursor.execute("DELETE FROM comments WHERE ogloszenie_id = %s", [ad_id])

            cursor.execute("DELETE FROM ads WHERE ad_id = %s", [ad_id])

        return JsonResponse({'message': 'Ogłoszenie zostało usunięte.'}, status=200)

    except Exception as e:
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
                cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
                result = cursor.fetchone()

                if not result:
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]

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

            return JsonResponse({'message': 'Ogłoszenie zostało zaktualizowane.'}, status=200)

        except Exception as e:
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


def przegladaj_ogloszenia_test(request):
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


def dodaj_komentarz(request, ad_id):
    '''
    Funkcja dodawania komenatrzy. Treść nie może być pusta.
    '''

    tresc = request.POST.get('tresc')
    uzytkownik_id = request.session.get('user_id')

    if not tresc or tresc.strip() == '':
        return JsonResponse({'error': 'Treść komentarza nie może być pusta.'}, status=400)

    sql = """
        INSERT INTO comments (ogloszenie_id, uzytkownik_id, tresc, data_utworzenia)
        VALUES (%s, %s, %s, CURRENT_DATE)
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [ad_id, uzytkownik_id, tresc])
        return JsonResponse({'message': 'Dodano komentarz.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def dodaj_komentarz_test(request, ad_id):
    return render(request, 'add_comment.html', {'ad_id': ad_id})


def edytuj_komentarz(request, comment_id):
    '''
    User moze edytowac tylko swoje komentarze. Admin moze edytkowac każdy komentarz. Treść nie może być pusta.
    '''
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Użytkownik niezalogowany.'}, status=401)

        tresc = request.POST.get('tresc')

        if not tresc or tresc.strip() == '':
            return JsonResponse({'error': 'Treść komentarza nie może być pusta.'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
                result = cursor.fetchone()

                if not result:
                    return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

                is_admin = result[0]

                cursor.execute("SELECT uzytkownik_id FROM comments WHERE comment_id = %s", [comment_id])
                comment_owner = cursor.fetchone()

                if not comment_owner:
                    return JsonResponse({'error': 'Komentarz nie istnieje.'}, status=404)

                if comment_owner[0] != user_id and not is_admin:
                    return JsonResponse({'error': 'Brak uprawnień do edytowania tego komentarza.'}, status=403)

                sql = """
                UPDATE comments SET tresc = %s, data_utworzenia = CURRENT_DATE
                WHERE comment_id = %s
                """
                cursor.execute(sql, [tresc, comment_id])

            return JsonResponse({'message': 'Komentarz został zaktualizowany.'}, status=200)

        except Exception as e:
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
            # Sprawdzamy, czy użytkownik jest administratorem
            cursor.execute("SELECT is_staff FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Zalogowany użytkownik nie istnieje.'}, status=404)

            is_admin = result[0]  # Zwróci wartość True (1) lub False (0)

            # Sprawdzamy, do kogo należy komentarz
            cursor.execute("SELECT uzytkownik_id FROM comments WHERE comment_id = %s", [comment_id])
            comment_owner = cursor.fetchone()

            if not comment_owner:
                return JsonResponse({'error': 'Komentarz nie istnieje.'}, status=404)

            # Jeśli użytkownik nie jest administratorem, sprawdzamy, czy jest właścicielem komentarza
            if comment_owner[0] != user_id and not is_admin:
                return JsonResponse({'error': 'Brak uprawnień do usunięcia tego komentarza.'}, status=403)

            # Jeśli uprawnienia są ok, usuwamy komentarz
            cursor.execute("DELETE FROM comments WHERE comment_id = %s", [comment_id])

        return JsonResponse({'message': 'Komentarz został usunięty.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def usun_komentarz_test(request, comment_id):
    return render(request, 'delete_comment.html', {'comment_id': comment_id})


def polub_ogloszenie(request, ad_id):
    uzytkownik_id = request.session.get('user_id')
    user_id = request.session.get('user_id')

    sql_check = "SELECT COUNT(*) FROM likes WHERE ogloszenie_id = %s AND uzytkownik_id = %s"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_check, [ad_id, uzytkownik_id])
            result = cursor.fetchone()
            if result[0] == 0:
                sql_insert = """
                    INSERT INTO likes (ogloszenie_id, uzytkownik_id)
                    VALUES (%s, %s)
                """
                cursor.execute(sql_insert, [ad_id, uzytkownik_id])

        return JsonResponse({'message': 'Polubiono ogłoszenie.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def polub_ogloszenie_test(request, ad_id):
    return render(request, 'like_ad.html', {'ad_id': ad_id})


def usun_polubienie(request, ad_id):
    uzytkownik_id = request.session.get('user_id')

    sql = "DELETE FROM likes WHERE ogloszenie_id = %s AND uzytkownik_id = %s"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [ad_id, uzytkownik_id])
        return JsonResponse({'message': 'Usunięto polubienie ogłoszenia.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Obsługa błędów


def usun_polubienie_test(request, ad_id):
    return render(request, 'dislike_ad.html', {'ad_id': ad_id})


def ocen_uzytkownika(request, oceniany_id):
    ocena = request.POST.get('ocena')
    oceniajacy_id = request.session.get('user_id')

    sql_insert = """
        INSERT INTO ratings (oceniajacy_id, oceniany_id, ocena, data_oceny)
        VALUES (%s, %s, %s, CURRENT_DATE)
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_insert, [oceniajacy_id, oceniany_id, ocena])
        return JsonResponse({'message': 'Oceniono użytkownika.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def ocen_uzytkownika_test(request, oceniany_id):
    return render(request, 'rate_user.html', {'oceniany_id': oceniany_id})


@admin_required
def dezaktywuj_uzytkownika(request, user_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET is_active = 0 WHERE user_id = %s"
            cursor.execute(sql, [user_id])

        return JsonResponse({
            'message': 'Użytkownik został dezaktywowany'}, status=200)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)



def dezaktywuj_uzytkownika_test(request, user_id):
    return render(request, 'admin/deactivate_user.html', {'user_id': user_id})


@admin_required
def aktywuj_uzytkownika(request, user_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET is_active = 1 WHERE user_id = %s"
            cursor.execute(sql, [user_id])

        return JsonResponse({
            'message': 'Użytkownik został aktywowany',
            'status': 'success'
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

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
