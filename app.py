from flask import Flask, render_template, request, jsonify
import duckdb
import os
import pandas as pd
from werkzeug.utils import secure_filename
import json

import mapa
from Funcoes_auxiliares import funcoesMongo

# Importações para a thread de relatórios
import threading
import time
from relatorio import gerar_relatorios_automaticamente

from Funcoes_auxiliares.InputMongo import InputMongo
from Funcoes_auxiliares.OutputMongo import OutputMongo

#---------------------------------------------------------------------
app = Flask(__name__)

# Conectar DuckDB
con = duckdb.connect()

# Carregar CSV em DuckDB
def carregar_tabela(nome_arquivo):
    caminho = os.path.join("Dados", nome_arquivo)
    try:
        # Forçar leitura limpa do cabeçalho
        df = pd.read_csv(caminho, encoding="utf-8-sig", sep=",", engine="python")
        
        # Renomear colunas removendo espaços ou caracteres invisíveis
        df.columns = [c.strip() for c in df.columns]

        # Substituir tabela no DuckDB
        con.unregister("dados") if "dados" in [t[0] for t in con.execute("SHOW TABLES").fetchall()] else None
        con.register("dados", df)
        print(f"[carregar_tabela] Colunas carregadas: {df.columns.tolist()}")
        
    except Exception as e:
        print(f"[ERRO] Falha ao carregar tabela {nome_arquivo}: {e}")
        raise



#---------------------------------------------------------------------
# Thread para gerar relatórios em segundo plano
def loop_relatorios():
    while True:
        gerar_relatorios_automaticamente()
        time.sleep(60)

threading.Thread(target=loop_relatorios, daemon=True).start()
RELATORIOS_DIR = "Relatorios"

'''
@app.route('/relatorios')
def relatorios():
    # lista os arquivos na pasta Relatorios
    arquivos = [f for f in os.listdir(RELATORIOS_DIR) if f.endswith(".jsonl")]
    return render_template("relatorios.html", arquivos=arquivos)
'''
@app.route("/relatorios")
def lista_relatorios():
    pasta = "Relatorios"
    try:
        arquivos = os.listdir(pasta)
        arquivos = [f for f in arquivos if os.path.isfile(os.path.join(pasta, f))]
        return jsonify({"arquivos": arquivos})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route("/relatorios")
def listar_relatorios():
    caminho = "Relatorios"
    if not os.path.exists(caminho):
        return []
    arquivos = [f for f in os.listdir(caminho) if f.endswith(".jsonl")]
    return arquivos

@app.route("/api/relatorios")
def api_relatorios():
    arquivos = listar_relatorios()
    return jsonify({"relatorios": arquivos})

def listar_arquivos_soa():
    caminho = "SOA"
    arquivos = [f for f in os.listdir(caminho) if f.endswith(".csv")]
    return arquivos

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
@app.route('/')
def index():
    arquivos_soa = listar_arquivos_soa()
    relatorios = listar_relatorios()
    return render_template('index.html', arquivos_soa=arquivos_soa, relatorios=relatorios)

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
@app.route("/visualizar_relatorio_terminal", methods=["POST"])
def visualizar_relatorio_terminal():
    data = request.get_json()
    nome = data.get("nome")
    
    if not nome:
        return jsonify({"result": "Nome do relatório não fornecido."}), 400

    caminho = os.path.join(RELATORIOS_DIR, nome)
    
    if not os.path.exists(caminho):
        return jsonify({"result": f"Arquivo '{nome}' não encontrado."}), 404

    print(f"\n\n==== Visualizando relatório: {nome} ====")
    conteudo = []
    try:
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                print(linha)
                conteudo.append(linha)
    except Exception as e:
        return jsonify({"result": f"Erro ao ler relatório: {e}"}), 500

    print("==== Fim do relatório ====\n\n")
    return jsonify({
        "result": f"Relatório '{nome}' impresso no terminal com sucesso.",
        "conteudo": conteudo
    })


#---------------------------------------------------------------------
# Envia dados para criar estatísticas
@app.route("/stats", methods=["GET"])
def stats():
    arquivo = request.args.get('arquivo')
    if not arquivo:
        return jsonify({"erro": "Arquivo não especificado"}), 400

    print(f"[stats] Arquivo solicitado: {arquivo}")

    # 1. Carregar base
    try:
        carregar_tabela(arquivo)
        print("[stats] tabela carregada com sucesso")
    except Exception as e:
        print("[stats] Erro ao carregar base:", e)
        return jsonify({"erro": f"Erro ao carregar CSV: {str(e)}"}), 400

    # 2. Ler dados
    try:
        df = con.execute("SELECT * FROM dados").fetchdf()
        print(f"[stats] número de registros na base: {len(df)}")
    except Exception as e:
        print("[stats] Erro ao ler dados da tabela 'dados':", e)
        return jsonify({"erro": f"Erro ao ler dados: {str(e)}"}), 500

    # caminho para ler cams.csv
    try:
        cams = pd.read_csv("cam_assets/cams.csv")
        print(f"[stats] cams.csv lido, colunas: {cams.columns.tolist()}")
    except Exception as e:
        print("[stats] Erro ao ler cams.csv:", e)
        return jsonify({"erro": f"Erro ao ler arquivo cams.csv: {str(e)}"}), 500

    # checar colunas necessárias
    required_cols = ['hash', 'horario_primeira_aparicao', 'numero_camera']
    for col in required_cols:
        if col not in df.columns:
            print(f"[stats] Coluna obrigatória ausente no evento: {col}, colunas disponíveis: {df.columns.tolist()}")
            return jsonify({"erro": f"Coluna obrigatória ausente: {col}", "colunas_disponiveis": df.columns.tolist()}), 400

    # Unir com cams
    try:
        df = df.merge(cams, left_on='numero_camera', right_on='Número da camera', how='left')
        print(f"[stats] merge com cams realizado, colunas agora: {df.columns.tolist()}")
    except Exception as e:
        print("[stats] Erro no merge com cams:", e)
        return jsonify({"erro": f"Erro no merge com cams.csv: {str(e)}"}), 500

    # conversão de data
    try:
        df['data'] = pd.to_datetime(df['horario_primeira_aparicao'], errors='coerce').dt.date
        print("[stats] coluna data criada com sucesso")
    except Exception as e:
        print("[stats] Erro ao converter horario_primeira_aparicao em data:", e)
        return jsonify({"erro": f"Erro ao converter data: {str(e)}"}), 500

    # Verificar colunas estacao e Linha
    if 'Estação' not in df.columns or 'Linha' not in df.columns or 'hash' not in df.columns:
        print(f"[stats] Colunas de estação ou linha ou hash faltando. Colunas do df: {df.columns.tolist()}")
        return jsonify({
            "erro": "Colunas esperadas não encontradas: 'Estação', 'Linha' ou 'hash'.",
            "colunas_disponiveis": df.columns.tolist()
        }), 400

    # Agora agrupar
    try:
        estacoes_por_dia = (
            df.groupby(['data', 'Estação'])['hash']
            .count()
            .reset_index(name='contagem')
            .sort_values('data')
        )
        linhas_por_dia = (
            df.groupby(['data', 'Linha'])['hash']
            .count()
            .reset_index(name='contagem')
            .sort_values('data')
        )
        print("[stats] agrupamentos por estação e linha feitos")
    except Exception as e:
        print("[stats] Erro no agrupamento:", e)
        return jsonify({"erro": f"Erro no agrupamento: {str(e)}"}), 500

    # rotas ok / erro — você pode ajustar a lógica real depois
    try:
        total_hashes = df['hash'].nunique()

        # Caminho do arquivo JSONL do relatório de erros (ajuste o caminho conforme seu projeto)
        nome_relatorio = f"relatorio_erros_{arquivo.replace('.csv','.jsonl')}"
        caminho_relatorio = os.path.join("Relatorios", nome_relatorio)

        hashes_com_erro = set()
        if os.path.exists(caminho_relatorio):
            with open(caminho_relatorio, encoding='utf-8') as f:
                for line in f:
                    try:
                        dado = json.loads(line)
                        hashes_com_erro.add(dado.get('hash'))
                    except:
                        pass

        rotas_erros = len(hashes_com_erro)
        rotas_ok = total_hashes - rotas_erros

        print(f"[stats] rotas_ok: {rotas_ok}, rotas_erros: {rotas_erros}")

    except Exception as e:
        print("[stats] Erro ao calcular rotas OK/Erro:", e)
        return jsonify({"erro": f"Erro ao calcular rotas: {str(e)}"}), 500

    except Exception as e:
        print("[stats] Erro ao contar rotas:", e)
        return jsonify({"erro": f"Erro ao contar rotas: {str(e)}"}), 500


    nome_db = nome_db = arquivo  # simples, mostra o nome do arquivo enviado

    return jsonify({
        "nomeDB": nome_db,
        "total": len(df),
        "total_trajetos": total_hashes,
        "estacoes_por_dia": estacoes_por_dia.to_dict(orient='records'),
        "linhas_por_dia": linhas_por_dia.to_dict(orient='records'),
        "rotas_ok": int(rotas_ok),
        "rotas_erros": int(rotas_erros)
    })

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
            cams_path = Path("cam_assets") / "cams.csv"
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
    gerar_grafo(numero_camera=numero_camera)

    return app.send_static_file("mapas/mapa.html")

#---------------------------------------------------------------------
@app.route("/hash_mapa")
def hash_mapa():
    from mapa import gerar_grafo_por_hash

    hash_val = request.args.get("hash")
    arquivo = request.args.get("arquivo", "movimentacao_pessoas_cameras.csv")

    if not hash_val:
        return "Hash não fornecida", 400

    try:
        carregar_tabela(arquivo)

        df = con.execute(f"""
            SELECT numero_camera 
            FROM dados 
            WHERE hash = '{hash_val}'
            ORDER BY horario_primeira_aparicao
        """).fetchdf()

        print("Câmeras encontradas para hash:", hash_val, df["numero_camera"].tolist())

        if df.empty:
            return f"Nenhuma câmera encontrada para a hash '{hash_val}'", 404

        caminho = gerar_grafo_por_hash(df["numero_camera"].tolist())
        return app.send_static_file("mapas/mapa.html")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Erro ao gerar mapa para hash: {e}", 500

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
#reseta dados de db do mongo
funcoesMongo.apagar_todos_documentos()
if __name__ == "__main__":
    # Inicia arquivos necessários
    #mapa.gerar_grafo()
    

    # Inicia as threads de input/output Mongo
    InputMongo(num_hashes=20, intervalo=5, lote_tamanho=10).start()
    OutputMongo(caminho_csv="Dados/mov_mongo_2025.csv", intervalo=10).start()

    # Inicia o servidor Flask
    app.run(debug=True)