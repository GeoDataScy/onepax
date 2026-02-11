import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

from controle_acesso.models import Catraca

print(f"{'ID (Identificador)':<20} | {'Nome':<30} | {'Tipo':<15}")
print("-" * 70)

for c in Catraca.objects.all():
    print(f"{c.identificador:<20} | {c.nome:<30} | {c.tipo:<15}")
