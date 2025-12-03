import requests
import time
import os
import pandas as pd
#---------------------------------------------------------------------------------------------
# python 'metodosValidacao/test_desempenho.py'
# URL base do servidor Flask
BASE_URL = "http://127.0.0.1:5000"

# Pasta onde estão as bases
PASTA_DADOS = "Dados"

resultados = []

for arquivo in os.listdir(PASTA_DADOS):
    if not arquivo.endswith(".csv"):
        continue
    
    caminho = os.path.join(PASTA_DADOS, arquivo)
    tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)

    print(f"\nTestando {arquivo} ({tamanho_mb:.2f} MB)")

    # Teste de carregamento
    inicio = time.time()
    r = requests.post(f"{BASE_URL}/carregar_base", data={"arquivo": arquivo})
    tempo_carregar = time.time() - inicio

    # Teste de consulta simples (exemplo)
    sql = "SELECT * FROM dados where numero_camera == 1"
    inicio = time.time()
    r = requests.post(f"{BASE_URL}/query", data={"sql": sql, "arquivo": arquivo})
    tempo_query = time.time() - inicio

    # Coletar número de linhas do arquivo
    try:
        df = pd.read_csv(caminho)
        linhas = len(df)
    except Exception:
        linhas = None

    resultados.append({
        "arquivo": arquivo,
        "tamanho_MB": round(tamanho_mb, 2),
        "linhas": linhas,
        "tempo_carregamento_s": round(tempo_carregar, 3),
        "tempo_consulta_s": round(tempo_query, 3)
    })

# Salvar resultados
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv("metodosValidacao/Resultados_testes_desempenho.csv", index=False)
print("\n✅ Testes concluídos! Resultados salvos em 'Resultados_testes_desempenho.csv'")
print(df_resultados)