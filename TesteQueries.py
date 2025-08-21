import duckdb
#----------------------------------------------------------
# Conectar
con = duckdb.connect()
# Ler CSV como tabela
tabela = 'Dados/movimentacao_pessoas_cameras.csv'
con.execute(f'CREATE TABLE dados AS SELECT * FROM read_csv_auto({tabela})')
#----------------------------------------------------------
# Queries Inputs:
sql = input("Query SQL: ")
try:
    # Tenta executar a consulta
    print(con.execute(sql).fetchdf())
except Exception as e:
    # erro
    print(f"Erro na consulta: {e}")

#----------------------------------------------------------
# Exemplos de queries:
# 1) Buscar tudo de uma pessoa
print(con.execute("""
SELECT * FROM dados
WHERE hash = '818257ed'
""").fetchdf()) # Precisa colocar entre aspas simples

# 2) Buscar por câmera
print(con.execute("""
SELECT * FROM dados
WHERE numero_camera = 2
""").fetchdf())

# 3) Pessoa em certo intervalo
print(con.execute("""
SELECT * FROM dados
WHERE hash = '818257ed'
AND horario_primeira_aparicao >= '2025-08-20 14:09:00'
AND horario_ultima_aparicao <= '2025-08-20 14:11:00'
""").fetchdf())


# 4) Buscar todas as aparições de uma pessoa em um único dia
print(con.execute("""SELECT * FROM dados
WHERE hash = '818257ed'
AND DATE(horario_primeira_aparicao) = '2025-08-20'
""").fetchdf())

# 5) Buscar todas as aparições de qualquer pessoa entre duas datas
print(con.execute("""
SELECT * FROM dados
WHERE horario_primeira_aparicao BETWEEN '2025-08-19' AND '2025-08-21'
""").fetchdf())

# 6) Buscar todas as aparições de uma câmera específica em certo dia
print(con.execute("""
SELECT * FROM dados
WHERE numero_camera = 2
AND DATE(horario_primeira_aparicao) = '2025-08-20'
""").fetchdf())

# 7) Buscar todas as pessoas que passaram por uma sequência de câmeras
print(con.execute("""
SELECT hash, COUNT(DISTINCT numero_camera) AS cameras_vistas
FROM dados
WHERE numero_camera IN (1, 2, 3, 4)
GROUP BY hash
HAVING COUNT(DISTINCT numero_camera) = 4
""").fetchdf())

# 8) Buscar o tempo de permanência de cada aparição
print(con.execute("""
SELECT *, horario_ultima_aparicao - horario_primeira_aparicao AS tempo_total
FROM dados
WHERE hash = '818257ed'
""").fetchdf())


# 9) Buscar a última aparição de uma pessoa
print(con.execute("""
SELECT *,SELECT *
FROM dados
WHERE hash = '818257ed'
ORDER BY horario_ultima_aparicao DESC
LIMIT 1
""").fetchdf())


# 10) Ver todos os horários em que uma pessoa foi vista em cada câmera
print(con.execute("""
SELECT numero_camera,
       MIN(horario_primeira_aparicao) AS primeira_vez,
       MAX(horario_ultima_aparicao) AS ultima_vez
FROM dados
WHERE hash = '818257ed'
GROUP BY numero_camera
ORDER BY numero_camera
""").fetchdf())


# 11) Ver quantas vezes cada pessoa apareceu (quantidade total de registros)
print(con.execute("""
SELECT numero_camera,
       MIN(horario_primeira_aparicao) AS primeira_vez,
       MAX(horario_ultima_aparicao) AS ultima_vez
FROM dados
WHERE hash = '818257ed'
GROUP BY numero_camera
ORDER BY numero_camera
""").fetchdf())


# Ver todas as pessoas que passaram por uma câmera específica em certo período
