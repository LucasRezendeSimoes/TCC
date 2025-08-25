# TCC

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
- duckdb - Executar SQL em Python
- flask - Comunicação Python/HTML
- pyvis - Gerar mapa

# Executar:
1. Rode app.py
2. Abra o link que o terminal fornecer (http://127.0.0.1:5000)