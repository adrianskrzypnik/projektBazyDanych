from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from datetime import datetime

from django.shortcuts import render
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

    return render(request, 'login.html')

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
    return render(request, 'edit_add.html', {'ad_id': ad_id})


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

def pobierz_uzytkownika(request, user_id):
    sql = """
    SELECT user_id, nazwa, email, data_utworzenia
    FROM users
    WHERE user_id = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id])
            row = cursor.fetchone()

        if row:
            user_data = {
                'user_id': row[0],
                'nazwa': row[1],
                'email': row[2],
                'data_utworzenia': row[3]
            }
            return JsonResponse(user_data, status=200)
        else:
            return JsonResponse({'error': 'Użytkownik nie znaleziony.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)