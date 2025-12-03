# TCC SUBWEYE

# Sobre o software:
O software desenvolvido realiza o processamento, análise, visualização e permite o fácil manuseio de dados provenientes de câmeras distribuídas em uma malha metroviária. Ele permite a ingestão de arquivos CSV, integração com MongoDB, validação de dados, geração de relatórios, reconstrução de trajetos e exibição interativa do grafo de câmeras em um mapa HTML. Além disso, oferece ferramentas de testes de desempenho, módulos auxiliares para manipulação de dados e uma interface web responsiva para consulta e exploração dos resultados.

# Desenvolvedores:
- Fernando Milani Venerando (RA: 24.122.063-1)
- Lucas Rezende Simões (RA: 24.122.028-4)

'8° semestre Ciências da Computação FEI - 2025'

# Estrutura do projeto:
## Árvore de diretórios:
/
├── app.py
├── mapa.py
├── relatorio.py
├── cam_assets/
│   ├── cams.csv
│   ├── grafo.csv
│   └── positions.csv
├── Dados/
│   └── mov_mongo_2025.csv
├── Funcoes_auxiliares/
│   ├── Conexao.py
│   ├── funcoesMongo.py
│   ├── geraDadosMongo.py
│   ├── InputMongo.py
│   └── OutputMongo.py
├── metodosValidacao/
│   ├── analise_desempenho.py
│   ├── test_desempenho.py
│   └── Resultados_testes_desempenho.csv
├── Relatorios/
├── SOA/
├── static/
│   ├── styles.css
│   └── script.js
└── templates/
    └── index.html

- ## app.py
Arquivo principal da aplicação. Responsável por inicializar o sistema, configurar rotas e integrar os módulos auxiliares.

## mapa.py
Implementa a lógica relacionada ao processamento e visualização do mapa (grafo de câmeras, rotas, posições e estrutura da rede).

## relatorio.py
Script destinado à geração de relatórios e análises, utilizado para inspeção de dados, validação e apoio ao desenvolvimento.

## cam_assets/
Armazena os arquivos base utilizados na construção do grafo de câmeras e na renderização do mapa.
### cams.csv
Lista de câmeras com identificadores e características.
### grafo.csv
Estrutura do grafo representando conexões entre câmeras.
### positions.csv
Posições das câmeras para visualização no mapa.

## Dados/
Lista de bases de dados
### mov_mongo_2025.csv
Base de dados remota vinculada ao MongoDB automaticamente

## Funcoes_auxiliares/
Contém módulos auxiliares que implementam funcionalidades de suporte, como conexão com banco, leitura e escrita de dados, geração de dados e consultas.
### Conexao.py
Gerencia a conexão com o banco de dados (MongoDB). Definição dos dados de acesso do banco remoto
### funcoesMongo.py
Implementa funções utilitárias para operações no MongoDB.
### geraDadosMongo.py
Insere dados no MongoDB para testes.
### InputMongo.py
Funções de ingestão e leitura de dados.
### OutputMongo.py
Gerenciamento de dados de saída e exportações.

## metodosValidacao/
Armazena scripts e resultados relacionados à validação de desempenho do sistema.
### analise_desempenho.py
Análise de performance.
### test_desempenho.py
Testes automatizados de desempenho.
### Resultados_testes_desempenho.csv
Métricas obtidas durante os testes.

## Relatorios/
Arquivos de relatório gerados a partir do processamento de dados, incluindo registros de inconsistências e erros.

## SOA/
Diretório reservado a arquivos referentes ao módulo ou etapa SOA (Arquitetura Orientada a Serviços) do projeto. É utilizado pela aplicação para listagem dinâmica de arquivos CSV destinados a testes ou entrada de dados

## static/
Componentes estáticos utilizados pela interface web da aplicação.
### styles.css
Folha de estilos.
### script.js
Lógica de interação da interface.

## templates/
Templates HTML utilizados pelo backend da aplicação (ex.: Flask).
### index.html
Página principal renderizada pelo sistema.


# Dependencias
- duckdb - Banco de dados em memória super rápido, usado para executar consultas SQL diretamente nos arquivos CSV
- flask - Framework web em Python, responsável pela comunicação entre o backend em Python e o frontend HTML
- pandas - Biblioteca para manipulação e análise de dados, usada pra transformar os resultados SQL em tabelas bem formatadas
- pyvis - Biblioteca de visualização de grafos, usada para gerar mapas interativos das câmeras e trajetos
- pymongo - Integração com banco de dados remoto MongoDB

# Executar:
1. Inatale as dependêencias (python -m pip install duckdb flask pandas pyvis pymongo)
2. Execute app.py
3. Abra o link que o terminal fornecer (http://127.0.0.1:5000)

# Possíveis implementações futuras:
### Redução da velocidade de consulta: Implementar otimizações de indexação e cache
para reduzir latência nas consultas, garantindo melhor desempenho em bases de grande escala.
### Obtenção de dados de outras fontes
Integrar novas origens de dados, como bilhetagem, catracas ou sensores complementares, ampliando a precisão e a contextualização das rotas analisadas.
### Uso de dados de distância reais entre câmeras: Incorporar medições físicas reais entre câmeras para aprimorar a validação temporal dos deslocamentos e aumentar a
fidelidade das estimativas de trajeto.
### Manipulação de dados do mapa pela interface: Permitir a edição direta do grafo,
incluindo criação e remoção de conexões ou câmeras, oferecendo maior autonomia ao usuário sem necessidade de alterar arquivos externos.
### Criação de bancos de dados remotos pela interface
Automatizar a configuração e criação de bancos remotos via interface, facilitando a implantação do sistema em ambientes distribuídos.
### Requisição de imagens capturadas
Habilitar a recuperação de imagens associadas às detecções, permitindo análises visuais e validação manual de trajetos dentro da própria plataforma