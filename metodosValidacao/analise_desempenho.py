import pandas as pd
#-----------------------------------------------------------
# python 'metodosValidacao/analise_desempenho.py'

# Caminho do arquivo único
CAMINHO_ARQUIVO = "metodosValidacao/Resultados_testes_desempenho.csv"

# Carregar o arquivo
df = pd.read_csv(CAMINHO_ARQUIVO)

# Calcular médias
media_carregamento = df["tempo_carregamento_s"].mean()
media_consulta = df["tempo_consulta_s"].mean()

# Correlação entre tamanho e tempo
corr_carregar = df["tamanho_MB"].corr(df["tempo_carregamento_s"])
corr_consulta = df["tamanho_MB"].corr(df["tempo_consulta_s"])

# Taxa de processamento (linhas por segundo)
df["taxa_carregamento"] = df["linhas"] / df["tempo_carregamento_s"]
df["taxa_consulta"] = df["linhas"] / df["tempo_consulta_s"]

media_taxa_carregar = df["taxa_carregamento"].mean()
media_taxa_consulta = df["taxa_consulta"].mean()

# Exibir resultados
print("\n===== RESULTADOS GERAIS =====")
print(f"Tempo médio de carregamento: {media_carregamento:.3f}s")
print(f"Tempo médio de consulta: {media_consulta:.3f}s")
print(f"Correlação tamanho <> carregamento: {corr_carregar:.3f}")
print(f"Correlação tamanho <> consulta: {corr_consulta:.3f}")
print(f"Taxa média de carregamento: {media_taxa_carregar:.1f} linhas/s")
print(f"Taxa média de consulta: {media_taxa_consulta:.1f} linhas/s")

print("\n===== DETALHES =====")
print(df[["arquivo","tamanho_MB","linhas","tempo_carregamento_s","tempo_consulta_s","taxa_consulta"]])