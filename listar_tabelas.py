import sqlite3
import os
import sys

# Redirecionar saída para arquivo
output_file = r'c:\PaxOne\tabelas_banco.txt'
sys.stdout = open(output_file, 'w', encoding='utf-8')

# Conectar ao banco de dados
db_path = r'c:\PaxOne\db.sqlite3'

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado em: {db_path}")
    sys.stdout.close()
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("=" * 100)
print("📊 TABELAS DO BANCO DE DADOS PAXONE")
print("=" * 100)
print()

if not tables:
    print("⚠️  Nenhuma tabela encontrada no banco de dados.")
else:
    print(f"Total de tabelas: {len(tables)}\n")
    
    for idx, (table_name,) in enumerate(tables, 1):
        print(f"{idx}. {table_name}")
        
        # Contar registros em cada tabela
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   └─ Registros: {count}")
        except Exception as e:
            print(f"   └─ Erro ao contar: {e}")
        
        print()

print("=" * 100)
print("\n📋 DETALHES DAS TABELAS PRINCIPAIS:\n")

# Tabelas do projeto (não Django admin)
project_tables = [t[0] for t in tables if not t[0].startswith('django_') and not t[0].startswith('auth_') and t[0] != 'sqlite_sequence']

for table_name in project_tables:
    print(f"\n🔹 Tabela: {table_name}")
    print("-" * 100)
    
    # Obter estrutura da tabela
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"{'PK':<4} {'ID':<5} {'Nome do Campo':<35} {'Tipo':<20} {'Null':<10} {'Default':<15}")
    print("-" * 100)
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        null_str = "NOT NULL" if not_null else "NULL"
        default_str = str(default_val) if default_val else "-"
        pk_marker = "🔑" if pk else ""
        print(f"{pk_marker:<4} {col_id:<5} {col_name:<35} {col_type:<20} {null_str:<10} {default_str:<15}")
    
    print()

conn.close()
print("\n✅ Análise concluída!")
print(f"\n📄 Resultado salvo em: {output_file}")

sys.stdout.close()

# Imprimir no console também
print("✅ Análise salva em tabelas_banco.txt", file=sys.__stdout__)
