import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT to_regclass('public.django_session');")
    exists = cursor.fetchone()[0]
    print(f"Tabela django_session existe? {exists}")
