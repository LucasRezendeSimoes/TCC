import pandas as pd
import random
import hashlib
from datetime import datetime, timedelta

def gerar_movimentacao_hashes(num_hashes=5, num_cameras=3, salvar_csv=True, caminho_csv="movimentacao_pessoas_cameras.csv"):
    """
    Gera movimentações de hashes entre múltiplas câmeras com timestamps coerentes.

    Parâmetros:
        num_hashes (int): Quantidade de pessoas/hashes a serem geradas.
        num_cameras (int): Quantidade de câmeras que cada pessoa passará.
        salvar_csv (bool): Se True, salva o resultado em um arquivo CSV.
        caminho_csv (str): Caminho do arquivo CSV para salvar os dados.

    Retorna:
        pd.DataFrame: DataFrame com os dados simulados.
    """
    
    def gerar_hash(index):
        return hashlib.md5(f"pessoa_{index}".encode()).hexdigest()[:8]

    def gerar_posicao():
        return f"({random.randint(0, 500)},{random.randint(0, 500)})"

    registros = []
    inicio = datetime(2025, 8, 20, 14, 0, 0)

    for i in range(num_hashes):
        pessoa_hash = gerar_hash(i)
        horario_atual = inicio + timedelta(minutes=random.randint(0, 10))
        duracao_camera = timedelta(seconds=random.randint(20, 40))

        for cam in range(1, num_cameras + 1):
            horario_inicio = horario_atual
            horario_fim = horario_inicio + duracao_camera
            posicao_inicio = gerar_posicao()
            posicao_fim = gerar_posicao()
            id_imagem = f"img_{random.randint(100, 999)}"

            registros.append({
                "hash": pessoa_hash,
                "horario_primeira_aparicao": horario_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                "horario_ultima_aparicao": horario_fim.strftime('%Y-%m-%d %H:%M:%S'),
                "posicao_inicial": posicao_inicio,
                "posicao_final": posicao_fim,
                "id_imagem": id_imagem,
                "numero_camera": cam
            })

            # Avança o tempo entre câmeras
            horario_atual = horario_fim + timedelta(seconds=random.randint(5, 15))

    df = pd.DataFrame(registros)

    if salvar_csv:
        df.to_csv(caminho_csv, index=False)
        print(f"CSV gerado com sucesso: {caminho_csv}")

    return df


# Exemplo de uso:
df = gerar_movimentacao_hashes(num_hashes=20, num_cameras=4)