from django.db import models

# =========================================================
# 1. TABELA DE EMBARQUE
# Baseado em: Embarque front end event_count.html
# =========================================================
class Embarque(models.Model):
    CLIENTE_CHOICES = [
        ('PRIO', 'PRIO'),
        ('PETROBRAS', 'PETROBRAS'),
        ('SPOT', 'SPOT'),
    ]

    # Dados do Voo
    flight_number = models.CharField(max_length=20, verbose_name="Nº do Voo")
    aeronave = models.CharField(max_length=10, verbose_name="Aeronave")
    operadora = models.CharField(max_length=100, verbose_name="Operador Aéreo")
    
    # Data e Hora (Separados conforme o HTML do front)
    departure_date = models.DateField(verbose_name="Data de Embarque")
    departure_time = models.TimeField(verbose_name="Hora do Embarque")
    
    # Localização
    platform = models.CharField(max_length=50, verbose_name="Plataforma")
    icao = models.CharField(max_length=10, verbose_name="ICAO")
    
    # Dados Comerciais
    cliente_final = models.CharField(max_length=50, choices=CLIENTE_CHOICES, verbose_name="Cliente Final")
    
    # Totais (Preenchido ao salvar o voo)
    passengers_boarded = models.IntegerField(default=0, verbose_name="Passageiros Embarcados")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    # Controle de Salvamento por Catraca (para consolidação)
    passageiros_catraca1 = models.IntegerField(default=0, verbose_name="Passageiros Catraca 1")
    passageiros_catraca2 = models.IntegerField(default=0, verbose_name="Passageiros Catraca 2")
    catraca1_salvo = models.BooleanField(default=False, verbose_name="Catraca 1 Salva")
    catraca2_salvo = models.BooleanField(default=False, verbose_name="Catraca 2 Salva")

    # Controle interno
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    def __str__(self):
        return f"Embarque {self.flight_number} - {self.aeronave}"

    class Meta:
        verbose_name = "Registro de Embarque"
        verbose_name_plural = "Registros de Embarque"


# =========================================================
# 2. TABELA DE DESEMBARQUE
# Baseado em: desembarque front end disembark_event_count.html
# =========================================================
class Desembarque(models.Model):
    CLIENTE_CHOICES = [
        ('PRIO', 'PRIO'),
        ('PETROBRAS', 'PETROBRAS'),
        ('SPOT', 'SPOT'),
    ]

    # Dados do Voo
    flight_number = models.CharField(max_length=20, verbose_name="Nº do Voo")
    aeronave = models.CharField(max_length=10, verbose_name="Aeronave")
    operadora = models.CharField(max_length=100, verbose_name="Operador Aéreo")
    
    # Data e Hora de Chegada
    arrival_date = models.DateField(verbose_name="Data de Chegada")
    arrival_time = models.TimeField(verbose_name="Hora de Chegada")
    
    # Origem (No desembarque geralmente é a Origem/Plataforma de onde veio)
    origin = models.CharField(max_length=100, verbose_name="Origem/Plataforma")
    
    # Dados Comerciais
    cliente_final = models.CharField(max_length=50, choices=CLIENTE_CHOICES, verbose_name="Cliente Final")
    
    # Totais
    passengers_disembarked = models.IntegerField(default=0, verbose_name="Passageiros Desembarcados")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    # Controle interno
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"Desembarque {self.flight_number} - {self.aeronave}"

    class Meta:
        verbose_name = "Registro de Desembarque"
        verbose_name_plural = "Registros de Desembarque"