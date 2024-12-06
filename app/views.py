from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from datetime import datetime


'''
Funkcja rejestracji użytkownika ze sprawdzeniem czy podany mail nie jest już wykorzystany
'''
def zarejestruj_uzytkownika(request):
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
    return render(request, 'register.html')

def zaloguj_uzytkownika(request):
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

def edytuj_profil(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        nazwa = request.POST.get('nazwa')
        email = request.POST.get('email')

        sql = "UPDATE users SET nazwa = %s, email = %s WHERE user_id = %s"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nazwa, email, user_id])

            return JsonResponse({'message': 'Profil został zaktualizowany.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def edytuj_profil_test(request):
    return render(request, 'edit_profile.html')

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
    user_id = request.session.get('user_id')
    sql = "DELETE FROM ads WHERE ad_id = %s AND uzytkownik_id = %s"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [ad_id, user_id])

        return JsonResponse({'message': 'Ogłoszenie zostało usunięte.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def usun_ogloszenie_test(request, ad_id):
    return render(request, 'delete_ad.html')


def edytuj_ogloszenie(request, ad_id):
    if request.method == 'POST':
        tytul = request.POST.get('tytul')
        opis = request.POST.get('opis')
        cena = request.POST.get('cena')
        kategoria_id = request.POST.get('kategoria_id')
        status = request.POST.get('status') == 'true'

        sql = """
        UPDATE ads SET tytul = %s, opis = %s, cena = %s, kategoria_id = %s, status = %s
        WHERE ad_id = %s
        """

        try:
            with connection.cursor() as cursor:
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
    tresc = request.POST.get('tresc')
    uzytkownik_id = request.session.get('user_id')

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
    tresc = request.POST.get('tresc')

    sql = """
        UPDATE comments
        SET tresc = %s, data_utworzenia = CURRENT_DATE
        WHERE comment_id = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [tresc, comment_id])
        return JsonResponse({'message': 'Komentarz został zaktualizowany.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Obsługa błędów

def edytuj_komentarz_test(request, comment_id):
    return render(request, 'edit_comment.html', {'comment_id': comment_id})


def usun_komentarz(request, comment_id):
    sql = "DELETE FROM comments WHERE comment_id = %s"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [comment_id])
        return JsonResponse({'message': 'Usunięto komentarz.'}, status=200)
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
