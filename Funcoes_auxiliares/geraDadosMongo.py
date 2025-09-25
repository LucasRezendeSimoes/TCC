# geraDadosMongo.py
import pandas as pd
import random
import hashlib
from datetime import datetime, timedelta
import os
from collections import defaultdict
import uuid
from Funcoes_auxiliares.Conexao import colecao

def obter_ultimo_horario():
    doc = colecao.find_one(sort=[("horario_ultima_aparicao", -1)])
    if doc:
        return datetime.strptime(doc["horario_ultima_aparicao"], '%Y-%m-%d %H:%M:%S')
    return datetime.now()

def gerar_movimentacao_realista(
    num_hashes=5,
    salvar_csv=True,
    caminho_csv="Dados/movimentacao_pessoas_cameras.csv",
    inicio_base=None,
    prob_erros=0.1
):
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

    grafo_df = pd.read_csv("Dados/grafo.csv")
    cams_df = pd.read_csv("Dados/cams.csv")
    cams_df.columns = ["numero_camera", "estacao", "linha", "tipo", "imagem_default"]

    grafo = defaultdict(list)
    for _, row in grafo_df.iterrows():
        origem = int(row["origem"])
        destino = int(row["destino"])
        grafo[origem].append(destino)
        grafo[destino].append(origem)

    cams_por_tipo = {
        "entrada": cams_df[cams_df["tipo"] == "entrada"]["numero_camera"].tolist(),
        "saida": cams_df[cams_df["tipo"] == "saída"]["numero_camera"].tolist(),
        "trajeto": cams_df[cams_df["tipo"] == "trajeto"]["numero_camera"].tolist()
    }

    def gerar_hash():
        return uuid.uuid4().hex[:8]

    def gerar_posicao():
        return f"({random.randint(0, 500)},{random.randint(0, 500)})"

    def gerar_id_imagem():
        return f"img_{random.randint(100, 999)}"

    def caminho_valido():
        tentativas = 0
        while tentativas < 50:
            inicio = random.choice(cams_por_tipo["entrada"])
            rota = [inicio]
            atual = inicio
            usados = {inicio}
            while len(rota) < 10:
                vizinhos = [v for v in grafo[atual] if v not in usados]
                if not vizinhos:
                    break
                proximo = random.choice(vizinhos)
                rota.append(proximo)
                usados.add(proximo)
                atual = proximo
                if atual in cams_por_tipo["saida"] and len(rota) >= 2:
                    return rota
            tentativas += 1
        return None

    def inserir_erros(rota):
        erro = random.random()
        if erro < prob_erros:
            tipo_erro = random.choice(["inicio", "fim", "buraco"])
            if tipo_erro == "inicio":
                rota[0] = random.choice(cams_df["numero_camera"].tolist())
            elif tipo_erro == "fim":
                rota[-1] = random.choice(cams_df["numero_camera"].tolist())
            elif tipo_erro == "buraco" and len(rota) >= 3:
                idx = random.randint(1, len(rota) - 2)
                rota[idx] = random.choice(cams_df["numero_camera"].tolist())
        return rota

    if inicio_base is None:
        inicio_base = obter_ultimo_horario()

    registros = []
    for i in range(num_hashes):
        trajeto = None
        while not trajeto:
            trajeto = caminho_valido()
        trajeto = inserir_erros(trajeto)
        pessoa_hash = gerar_hash()

        tempo_atual = inicio_base + timedelta(seconds=1)
        for cam_id in trajeto:
            duracao = timedelta(seconds=random.randint(20, 40))
            fim = tempo_atual + duracao
            registros.append({
                "hash": pessoa_hash,
                "horario_primeira_aparicao": tempo_atual.strftime('%Y-%m-%d %H:%M:%S'),
                "horario_ultima_aparicao": fim.strftime('%Y-%m-%d %H:%M:%S'),
                "posicao_inicial": gerar_posicao(),
                "posicao_final": gerar_posicao(),
                "id_imagem": gerar_id_imagem(),
                "numero_camera": cam_id
            })
            tempo_atual = fim + timedelta(seconds=random.randint(5, 15))
        inicio_base = tempo_atual + timedelta(minutes=1)

    df = pd.DataFrame(registros)
    if salvar_csv:
        df.to_csv(caminho_csv, index=False)
        print(f"CSV gerado com sucesso: {caminho_csv}")

    return df