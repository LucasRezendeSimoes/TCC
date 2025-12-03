# python -m Funcoes_auxiliares.funcoesMongo
from Funcoes_auxiliares.Conexao import colecao
import glob, os

# Apaga conteúdo da DB, relatórios e limpa o CSV
def apagar_todos_documentos():
    # Apaga documentos do MongoDB
    resultado = colecao.delete_many({})
    print(f"{resultado.deleted_count} documentos do cluster apagados")

    # Apaga todas as linhas do CSV, exceto a primeira
    caminho_arquivo = 'Dados/mov_mongo_2025.csv'
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            if linhas:
                arquivo.write(linhas[0])  # Mantém apenas o cabeçalho

        print(f"Arquivo '{caminho_arquivo}' limpo, mantendo apenas o cabeçalho.")
    except FileNotFoundError:
        print(f"Arquivo '{caminho_arquivo}' não encontrado.")
    except Exception as e:
        print(f"Erro ao limpar o arquivo: {e}")

    #  arquivos .jsonl da pasta Relatorios
    pasta_relatorios = 'Relatorios'
    try:
        arquivos_jsonl = glob.glob(os.path.join(pasta_relatorios, '*.jsonl'))
        for arquivo in arquivos_jsonl:
            os.remove(arquivo)
        print(f"{len(arquivos_jsonl)} arquivos .jsonl removidos da pasta '{pasta_relatorios}'.")
    except Exception as e:
        print(f"Erro ao remover arquivos .jsonl: {e}")

    # limpar conteúdo de bases_processadas.txt
    caminho_bases = os.path.join(pasta_relatorios, 'bases_processadas.txt')
    try:
        with open(caminho_bases, 'w', encoding='utf-8') as arquivo:
            arquivo.truncate(0)  # Limpa o conteúdo do arquivo
        print(f"Conteúdo de '{caminho_bases}' apagado com sucesso.")
    except FileNotFoundError:
        print(f"Arquivo '{caminho_bases}' não encontrado.")
    except Exception as e:
        print(f"Erro ao limpar '{caminho_bases}': {e}")

# Executa a função
apagar_todos_documentos()