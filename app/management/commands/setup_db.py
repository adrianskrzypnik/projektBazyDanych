from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Ustawienia bazy danych'

    def handle(self, *args, **kwargs):
        sql_file_path = 'sql/setup.sql'
        try:
            with open(sql_file_path, 'r') as sql_file:
                sql_commands = sql_file.read()
            with connection.cursor() as cursor:
                cursor.execute(sql_commands)
            self.stdout.write(self.style.SUCCESS('Baza danych została zainicjalizowana!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Błąd podczas inicjalizacji bazy danych: {e}'))
