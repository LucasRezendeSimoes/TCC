from flask import Flask, render_template, request, jsonify
import duckdb
import os
import pandas as pd
from werkzeug.utils import secure_filename
#---------------------------------------------------------------------
app = Flask(__name__)

# Conectar DuckDB
con = duckdb.connect()

# Carregar CSV em DuckDB
def carregar_tabela(nome_arquivo):
    caminho = os.path.join("Dados", nome_arquivo)
    con.execute(f"""
        CREATE OR REPLACE TABLE dados AS 
        SELECT * FROM read_csv_auto('{caminho}')
    """)

#---------------------------------------------------------------------
@app.route("/carregar_base", methods=["POST"])
def carregar_base():
    arquivo = request.form.get("arquivo")
    try:
        carregar_tabela(arquivo)
        df = con.execute("SELECT * FROM dados").fetchdf()
        linhas = len(df)
        result_str = f"{linhas} resultado(s) encontrado(s)\n\n" + df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro ao carregar base: {e}"})

#---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

#---------------------------------------------------------------------
@app.route("/query", methods=["POST"])
def query():
    sql = request.form.get("sql")
    arquivo = request.form.get("arquivo")

    print("Recebi SQL:", sql)
    print("Arquivo selecionado:", arquivo)

    try:
        carregar_tabela(arquivo)
        df = con.execute(sql).fetchdf()
        linhas = len(df)
        result_str = f"{linhas} resultado(s) encontrado(s)\n\n" + df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro na consulta: {e}"})

#---------------------------------------------------------------------
@app.route("/auto_query", methods=["POST"])
def auto_query():
    from pathlib import Path

    hash_val = request.form.get("hash")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")
    numero_camera = request.form.get("numero_camera")
    linha = request.form.get("linha")
    estacao = request.form.get("estacao")
    arquivo = request.form.get("arquivo")

    def format_datetime(dt_str):
        if dt_str and "T" in dt_str:
            return dt_str.replace("T", " ") + ":00"
        return dt_str

    inicio = format_datetime(inicio)
    fim = format_datetime(fim)

    try:
        carregar_tabela(arquivo)
    except Exception as e:
        return jsonify({"result": f"Erro ao carregar arquivo de movimentação: {e}"})

    where_clauses = []

    if hash_val:
        where_clauses.append(f"hash = '{hash_val}'")

    if numero_camera:
        where_clauses.append(f"numero_camera = {numero_camera}")

    cameras_filtradas = None
    if linha or estacao:
        try:
            cams_path = Path("Dados") / "cams.csv"
            cams_df = pd.read_csv(cams_path)

            filtro = pd.Series([True] * len(cams_df))
            if linha:
                filtro &= cams_df["Linha"].str.lower() == linha.lower()
            if estacao:
                filtro &= cams_df["Estação"].str.lower() == estacao.lower()

            cameras_filtradas = cams_df.loc[filtro, "Número da camera"].tolist()

            if not cameras_filtradas:
                return jsonify({"result": f"Nenhuma câmera encontrada para linha='{linha}' e estação='{estacao}'."})

            where_clauses.append(f"numero_camera IN ({','.join(map(str, cameras_filtradas))})")

        except Exception as e:
            return jsonify({"result": f"Erro ao consultar cams.csv: {e}"})

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
        linhas = len(df)
        result_str = f"{linhas} resultado(s) encontrado(s)\n\n" + df.to_string(index=False)
        return jsonify({"result": result_str})
    except Exception as e:
        return jsonify({"result": f"Erro na consulta: {e}"})

#---------------------------------------------------------------------
@app.route("/arquivos")
def arquivos():
    pasta = "Dados"
    try:
        arquivos = os.listdir(pasta)
        arquivos = [f for f in arquivos if os.path.isfile(os.path.join(pasta, f))]
        return jsonify({"arquivos": arquivos})
    except Exception as e:
        return jsonify({"erro": str(e)})

#---------------------------------------------------------------------
@app.route("/mapa")
def mapa():
    from mapa import gerar_grafo

    numero_camera = request.args.get("numero_camera")
    gerar_grafo(numero_camera=numero_camera)  # passa para o mapa.py

    return app.send_static_file("mapas/mapa.html")


#---------------------------------------------------------------------
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    if "arquivo_csv" not in request.files:
        return jsonify({"result": "Nenhum arquivo enviado."})

    file = request.files["arquivo_csv"]
    if file.filename == "":
        return jsonify({"result": "Nome de arquivo vazio."})

    if not file.filename.endswith(".csv"):
        return jsonify({"result": "Formato inválido. Envie um .csv."})

    try:
        filename = secure_filename(file.filename)
        destino = os.path.join("Dados", filename)
        file.save(destino)
        return jsonify({"result": f"Arquivo '{filename}' enviado com sucesso."})
    except Exception as e:
        return jsonify({"result": f"Erro ao salvar arquivo: {e}"})


#---------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
