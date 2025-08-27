# TCC

# Desenvolvedores:
- Fernando Milani Venerando (RA: 24.122.063-1)
- Lucas Rezende Simões (RA: 24.122.028-4)
'8° semestre Ciências da Computação FEI - 2025'

# Brainstorm:
- Lod Câmera/Estação
- Mostrar tabela Inteira com query destacada/ Mostrar apenas query
- Pesquisa por linha e estação
- Informações contidas em cada câmera:
  - Número da camera
  - Estação e linha
  - Câmeras conectadas no grafo/mapa
  - Camera de entrada/trajeto/saída
  - Imagem default
- Destaque do mapa:
  - Desque de rota:
    1. Query de hash
    2. Verifica todas as aparições da hash
    3. Lista câmeras de aparição e ordena por tempo inicial
    4. Compara ordem com conexções do grafo no mapa
      - Se estiver OK:
        1. destaque no mapa os vertices correspondentes e as conexões entre eles
      - Se não foi detectado entrando:
        1. Se o primeiro registro da hash não foi de uma câmera de entrada, detectar câmera de entrada mais próxima de primeiro registro
        2. Destacar no mapa vertices e conexões entre eles percorridos
        3. destacar (de forma diferente) trajeto e vertice mais provavel entre camera de entrada mais próxima e camera de primeiro registro
        4. Enviar para relatório de discrepancias
      - Se tem buracos no meio do trajeto:
        1. Se em meio ao trajeto da hash estiver faltando uma ou mais , detectar trajeto mais curto entre buracos
        2. Destacar no mapa vertices e conexões entre eles percorridos
        3. destacar (de forma diferente) trajeto e vertice mais provavel entre buracos
        4. Enviar para relatório de discrepancias
      - Se não foi detectado saindo:
        1. Se o último registro da hash não foi de uma câmera de saída, detectar câmera de saída mais próxima de último registro
        2. Destacar no mapa vertices e conexões entre eles percorridos
        3. destacar (de forma diferente) trajeto e vertice mais provavel entre camera de saída mais próxima e camera de último registro
        4. Enviar para relatório de discrepancias
  - Destaque de camera:
    1. Query de camera
    2. Destacar camera no mapa
  - Destaque de estacao:
    1. Query de estacao
    2. Destacar todas os vertices e arestas da estacao correspondente
  - Destqeue de Linha:
    1. Query de linha
    2. Destacar todos os vertices e arestas da linha correspondente (Destacar da cor correspondentte da linha)


# Implementações:
## Implementações para fazer:
- Exportar log
- Contagem de linhas do resultado da pesquisa
- Diferenciação de log inválido e válido mas com 0 resultados
- Importar e exportar Mapas
- Importar e exportar DB

## Implementações feitas:
- Função que gera dados para testes
- Página HTML
- Queries automatizadas (Tempo inicial, tempo final, intervalo de tempo, NCamera e hash) [Pesquisa por localizações são referenciadas pela posição da camera]
- Prompt SQL para queries mais expecíficas
- Listagem de arquivos em "Dados"
- Referência de DB selecionada
- Construção do mapa

# Dependencias
* 'python -m pip install duckdb flask pandas pyvis'
- duckdb - Banco de dados em memória super rápido, usado para executar consultas SQL diretamente nos arquivos CSV
- flask - Framework web em Python, responsável pela comunicação entre o backend em Python e o frontend HTML
- pandas - Biblioteca para manipulação e análise de dados, usada pra transformar os resultados SQL em tabelas bem formatadas
- pyvis - Biblioteca de visualização de grafos, usada para gerar mapas interativos das câmeras e trajetos

# Executar:
1. Inatale as dependêencias
2. Rode app.py
3. Abra o link que o terminal fornecer (http://127.0.0.1:5000)