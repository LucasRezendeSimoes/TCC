from flask import Flask, render_template, request, jsonify
import duckdb
import os

app = Flask(__name__)

# Conectar DuckDB
con = duckdb.connect()


# Conectar DuckDB e carregar CSV em tabela
def carregar_tabela(nome_arquivo):
    caminho = os.path.join("Dados", nome_arquivo)
    con.execute(f"""
        CREATE OR REPLACE TABLE dados AS 
        SELECT * FROM read_csv_auto('{caminho}')
    """)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    sql = request.form.get("sql")
    arquivo = request.form.get("arquivo")

    print("Recebi SQL:", sql)
    print("Arquivo selecionado:", arquivo)

    try:
        carregar_tabela(arquivo)
        df = con.execute(sql).fetchdf()
        result_str = df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro na consulta: {e}"})



@app.route("/auto_query", methods=["POST"])
def auto_query():
    hash_val = request.form.get("hash")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")
    numero_camera = request.form.get("numero_camera")
    arquivo = request.form.get("arquivo")

    try:
        carregar_tabela(arquivo)
    except Exception as e:
        return jsonify({"result": f"Erro ao carregar arquivo: {e}"})

    def format_datetime(dt_str):
        if dt_str and "T" in dt_str:
            return dt_str.replace("T", " ") + ":00"
        return dt_str

    inicio = format_datetime(inicio)
    fim = format_datetime(fim)

    where_clauses = []

    if hash_val:
        where_clauses.append(f"hash = '{hash_val}'")

    if numero_camera:
        where_clauses.append(f"numero_camera = {numero_camera}")

    coluna_data = "horario_primeira_aparicao"

    if inicio and fim:
        where_clauses.append(f"{coluna_data} BETWEEN '{inicio}' AND '{fim}'")
    elif inicio:
        where_clauses.append(f"{coluna_data} = '{inicio}'")
    elif fim:
        where_clauses.append(f"{coluna_data} = '{fim}'")

    sql = "SELECT * FROM dados"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    print("Consulta montada:", sql)

    try:
        df = con.execute(sql).fetchdf()
        result_str = df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro na consulta: {e}"})

    hash_val = request.form.get("hash")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")
    numero_camera = request.form.get("numero_camera")

    # Corrigir o formato da data para 'YYYY-MM-DD HH:MM:00'
    def format_datetime(dt_str):
        if dt_str and "T" in dt_str:
            return dt_str.replace("T", " ") + ":00"
        return dt_str

    inicio = format_datetime(inicio)
    fim = format_datetime(fim)

    where_clauses = []

    if hash_val:
        where_clauses.append(f"hash = '{hash_val}'")

    if numero_camera:
        where_clauses.append(f"numero_camera = {numero_camera}")

    # Usar a coluna de horário correta
    coluna_data = "horario_primeira_aparicao"

    if inicio and fim:
        where_clauses.append(f"{coluna_data} BETWEEN '{inicio}' AND '{fim}'")
    elif inicio:
        where_clauses.append(f"{coluna_data} = '{inicio}'")
    elif fim:
        where_clauses.append(f"{coluna_data} = '{fim}'")

    sql = "SELECT * FROM dados"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    print("Consulta montada:", sql)

    try:
        df = con.execute(sql).fetchdf()
        result_str = df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro na consulta: {e}"})

# Envia arquivos da pasta Dados
@app.route("/arquivos")
def arquivos():
    pasta = "Dados"
    try:
        arquivos = os.listdir(pasta)
        arquivos = [f for f in arquivos if os.path.isfile(os.path.join(pasta, f))]
        return jsonify({"arquivos": arquivos})
    except Exception as e:
        return jsonify({"erro": str(e)})
    

# gera mapa
@app.route("/mapa")
def mapa():
    from mapa import gerar_grafo  # ou grafo.py, depende do seu nome
    gerar_grafo()
    return app.send_static_file("mapas/mapa.html")



#-------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)