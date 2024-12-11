from django.db import connection
from functools import wraps
from django.http import JsonResponse

def is_admin(user_id):
    """
    Sprawdza w bazie danych, czy użytkownik ma uprawnienia administratora, używając raw SQL.
    """
    print(user_id)
    if not user_id:
        return False

    sql = "SELECT is_staff FROM users WHERE user_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id])
            result = cursor.fetchone()
            print(result)
            if result:
                return result[0]  # Zwraca True, jeśli is_staff = 1
            return False
    except Exception as e:
        # Możesz dodać logowanie błędu, jeśli zajdzie potrzeba
        return False

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')


        if not is_admin(user_id):
            return JsonResponse({
                'error': 'Brak uprawnień administratora',
                'status': 'forbidden'
            }, status=403)
        return view_func(request, *args, **kwargs)

    return wrapper
