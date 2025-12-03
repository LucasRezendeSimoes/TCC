import os
import csv
import json
import networkx as nx
from datetime import datetime

DADOS_DIR = "Dados"
RELATORIOS_DIR = "Relatorios"
CAMERAS_CSV = os.path.join("cam_assets", "cams.csv")
GRAFO_CSV = os.path.join("cam_assets", "grafo.csv")
PROCESSED_LOG = os.path.join(RELATORIOS_DIR, "bases_processadas.txt")

os.makedirs(RELATORIOS_DIR, exist_ok=True)
#--------------------------------------------------------------------------

def analisar_base(movimento_csv):
    nome_base = os.path.basename(movimento_csv)
    relatorio_path = os.path.join(RELATORIOS_DIR, f"relatorio_erros_{nome_base.replace('.csv','.jsonl')}")

    # Grafo de conexões válidas
    G = nx.Graph()
    with open(GRAFO_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                origem = int(row['origem'])
                destino = int(row['destino'])
                if not destino:  # evitar linhas com destino vazio
                    continue
                G.add_edge(origem, destino)
            except:
                continue

    # Mapeamento de tipo das câmeras
    cameras_tipo = {}
    with open(CAMERAS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                num = int(row['Número da camera'])
                tipo = row.get('Tipo', '').strip().lower()
                cameras_tipo[num] = tipo
            except:
                continue

    # Agrupar eventos por hash
    hash_map = {}
    with open(movimento_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hash_id = row['hash']
            camera = int(row['numero_camera'])
            img_id = row.get('id_imagem', None)
            inicio = row.get('horario_primeira_aparicao')
            fim = row.get('horario_ultima_aparicao')

            if hash_id not in hash_map:
                hash_map[hash_id] = {
                    "eventos": [],
                }

            hash_map[hash_id]["eventos"].append({
                "camera": camera,
                "imagem": img_id,
                "inicio": inicio,
                "fim": fim
            })

    # Analisar cada hash
    with open(relatorio_path, "w", encoding="utf-8") as outfile:
        for hash_id, dados in hash_map.items():
            eventos = sorted(dados["eventos"], key=lambda e: e["inicio"] or "")
            trajeto = [e["camera"] for e in eventos]
            imagens = [e["imagem"] for e in eventos]
            horarios_inicio = [e["inicio"] for e in eventos if e["inicio"]]
            horarios_fim = [e["fim"] for e in eventos if e["fim"]]

            tipo_erro = []
            cameras_deduzidas = []
            caminho_final = trajeto.copy()

            # Verificação de entrada
            primeira = trajeto[0]
            if cameras_tipo.get(primeira, "") != "entrada":
                tipo_erro.append("sem_entrada")
                # Deduza a entrada mais próxima
                entradas_possiveis = [c for c, t in cameras_tipo.items() if t == "entrada"]
                try:
                    caminhos = [nx.shortest_path(G, source=e, target=primeira) for e in entradas_possiveis]
                    melhor = min(caminhos, key=len)
                    cameras_deduzidas += melhor[:-1]  # sem repetir o primeiro do trajeto
                    caminho_final = melhor[:-1] + caminho_final
                except:
                    tipo_erro.append("entrada_impossivel")

            # Verificação de saída
            ultima = trajeto[-1]
            if cameras_tipo.get(ultima, "") != "saída":
                tipo_erro.append("sem_saida")
                # Deduza a saída mais próxima
                saidas_possiveis = [c for c, t in cameras_tipo.items() if t == "saída"]
                try:
                    caminhos = [nx.shortest_path(G, source=ultima, target=s) for s in saidas_possiveis]
                    melhor = min(caminhos, key=len)
                    cameras_deduzidas += melhor[1:]  # evita repetir ultima
                    caminho_final = caminho_final + melhor[1:]
                except:
                    tipo_erro.append("saida_impossivel")

            # Verificação de buracos
            trajeto_completo = caminho_final.copy()
            for i in range(len(trajeto_completo) - 1):
                a, b = trajeto_completo[i], trajeto_completo[i + 1]
                if not G.has_edge(a, b):
                    try:
                        path = nx.shortest_path(G, source=a, target=b)
                        if path[1:-1]:
                            cameras_deduzidas.extend(path[1:-1])
                            tipo_erro.append("buraco_trajeto")

                            # Substitui o par (a, b) por todo o caminho deduzido
                            trajeto_completo = caminho_final.copy()
                            caminho_final = trajeto_completo[:i+1] + path[1:-1] + trajeto_completo[i+1:]

                    except nx.NetworkXNoPath:
                        tipo_erro.append("trajeto_impossivel")

            # Apenas registrar hashes com erro
            if tipo_erro:
                json.dump({
                    "hash": hash_id,
                    "base": nome_base,
                    "tipo_erro": list(set(tipo_erro)),
                    "cameras_": trajeto,
                    #"cameras_provaveis": list(set(cameras_deduzidas)),
                    "cameras_provaveis": list(dict.fromkeys(cameras_deduzidas)),
                    "entrada_esperada": [c for c, t in cameras_tipo.items() if t == "entrada"],
                    "saida_esperada": [c for c, t in cameras_tipo.items() if t == "saída"],
                    "horario_primeira_aparicao": horarios_inicio[0] if horarios_inicio else None,
                    "horario_ultima_aparicao": horarios_fim[-1] if horarios_fim else None,
                    "imagens": imagens,
                    "caminho_provavel": caminho_final
                }, outfile)
                outfile.write("\n")


def gerar_relatorios_automaticamente():
    bases_processadas = set()
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, "r") as f:
            bases_processadas = set(l.strip() for l in f.readlines())

    for arquivo in os.listdir(DADOS_DIR):
        if arquivo.endswith(".csv") and arquivo.startswith("mov"):
            if arquivo not in bases_processadas:
                print(f"Processando {arquivo}...")
                try:
                    analisar_base(os.path.join(DADOS_DIR, arquivo))
                    with open(PROCESSED_LOG, "a") as logf:
                        logf.write(arquivo + "\n")
                except Exception as e:
                    print(f"Erro ao processar {arquivo}: {e}")
