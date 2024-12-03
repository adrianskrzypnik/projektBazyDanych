from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from datetime import datetime

def zarejestruj_uzytkownika(request):
    if request.method == 'POST':
        nazwa = request.POST.get('nazwa')
        email = request.POST.get('email')
        haslo = request.POST.get('haslo')
        data_utworzenia = datetime.now()

        sql = """
        INSERT INTO users (nazwa, email, haslo, data_utworzenia)
        VALUES (%s, %s, %s, %s)
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nazwa, email, haslo, data_utworzenia])

            return JsonResponse({'message': 'Użytkownik został zarejestrowany.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'zarejestruj.html')



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
            # Konwersja wyniku na słownik
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
#cos