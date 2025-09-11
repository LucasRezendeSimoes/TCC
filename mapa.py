from pyvis.network import Network
import os
import csv
import networkx as nx

def gerar_grafo(numero_camera=None):
    try:
        if numero_camera:
            numero_camera = int(numero_camera)
    except:
        numero_camera = None

    net = Network(height="500px", width="100%", directed=False, bgcolor="#495057", font_color="white")

    caminho_csv = os.path.join("Dados", "cams.csv")
    dados_cameras = {}
    if os.path.exists(caminho_csv):
        with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    numero = int(row.get('Número da camera') or row.get('Número da câmera'))
                    dados_cameras[numero] = row
                except:
                    continue

    for cam_num, cam_data in dados_cameras.items():
        estacao = cam_data.get("Estação", "Desconhecida")
        linha = cam_data.get("Linha", "Desconhecida")
        tipo = cam_data.get("Tipo", "Desconhecido")

        title = f"Câmera {cam_num}\nEstação: {estacao}\nLinha: {linha}\nTipo: {tipo}"

        net.add_node(
            cam_num,
            label=f"Câmera {cam_num}",
            title=title,
            x=cam_num * 200 - 200,
            y=0,
            fixed=True,
            color="orange" if cam_num == numero_camera else "white",
            size=10 if cam_num == numero_camera else 5
        )

    conexoes_validas = carregar_conexoes_validas()
    for origem, destino in conexoes_validas:
        net.add_edge(origem, destino, color="#C9C9C9", width=1, smooth={"type": "curvedCW", "roundness": 0.3}, arrows='false')

    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")
    net.write_html(caminho_html, notebook=False)
    _injetar_legenda_no_html(caminho_html)

    return caminho_html


def gerar_grafo_por_hash(lista_cameras):
    net = Network(height="380px", width="50%", directed=True, bgcolor="#495057", font_color="white")

    caminho_csv = os.path.join("Dados", "cams.csv")
    dados_cameras = {}
    if os.path.exists(caminho_csv):
        with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    numero = int(row.get('Número da camera') or row.get('Número da câmera'))
                    dados_cameras[numero] = row
                except:
                    continue

    conexoes_validas = carregar_conexoes_validas()
    G = nx.Graph()
    G.add_edges_from(conexoes_validas)

    # Cálculo das entradas próximas (múltiplas possíveis) para o início do trajeto
    entradas_proximas = []
    caminho_extra_inicio = []
    primeiro = lista_cameras[0]
    tipo_primeiro = dados_cameras.get(primeiro, {}).get("Tipo", "").lower()
    if tipo_primeiro != "entrada":
        entradas = [cam for cam, data in dados_cameras.items() if data.get("Tipo", "").lower() == "entrada"]
        distancias_caminhos = []
        for entrada in entradas:
            try:
                caminho = nx.shortest_path(G, source=entrada, target=primeiro)
                distancias_caminhos.append((len(caminho), caminho))
            except nx.NetworkXNoPath:
                continue
        if distancias_caminhos:
            menor_dist = min(d[0] for d in distancias_caminhos)
            # Filtra todos os caminhos com essa menor distância
            caminhos_menores = [c for dist, c in distancias_caminhos if dist == menor_dist]
            entradas_proximas = [c[0] for c in caminhos_menores]
            # Pega o primeiro caminho para construir a rota extra (pode ser qualquer)
            caminho_extra_inicio = caminhos_menores[0][:-1]

    # Cálculo das saídas próximas (múltiplas possíveis) para o fim do trajeto
    saidas_proximas = []
    caminho_extra_fim = []
    ultimo = lista_cameras[-1]
    tipo_ultimo = dados_cameras.get(ultimo, {}).get("Tipo", "").lower()
    if tipo_ultimo != "saída":
        saidas = [cam for cam, data in dados_cameras.items() if data.get("Tipo", "").lower() == "saída"]
        distancias_caminhos = []
        for saida in saidas:
            try:
                caminho = nx.shortest_path(G, source=ultimo, target=saida)
                distancias_caminhos.append((len(caminho), caminho))
            except nx.NetworkXNoPath:
                continue
        if distancias_caminhos:
            menor_dist = min(d[0] for d in distancias_caminhos)
            caminhos_menores = [c for dist, c in distancias_caminhos if dist == menor_dist]
            saidas_proximas = [c[-1] for c in caminhos_menores]
            caminho_extra_fim = caminhos_menores[0][1:]

    lista_final = caminho_extra_inicio + lista_cameras + caminho_extra_fim
    cameras_hash = set(lista_cameras)
    cameras_deduzidas = set(caminho_extra_inicio + caminho_extra_fim)

    for cam_num, cam_data in dados_cameras.items():
        estacao = cam_data.get("Estação", "Desconhecida")
        linha = cam_data.get("Linha", "Desconhecida")
        tipo = cam_data.get("Tipo", "Desconhecido")

        title = f"Câmera {cam_num}\nEstação: {estacao}\nLinha: {linha}\nTipo: {tipo}"

        if cam_num in cameras_hash:
            color = "red"  # Câmera percorrida
            size = 15
        elif cam_num in cameras_deduzidas:
            color = "green"  # Câmera deduzida para completar caminho
            size = 12
        elif cam_num in entradas_proximas:
            color = "blue"  # Entradas próximas possíveis
            size = 12
        elif cam_num in saidas_proximas:
            color = "blue"  # Saídas próximas possíveis
            size = 12
        else:
            color = "white"
            size = 7

        net.add_node(
            cam_num,
            label=f"Câmera {cam_num}",
            title=title,
            color=color,
            size=size,
            x=cam_num * 200,
            y=0,
            fixed=True
        )

    for origem, destino in conexoes_validas:
        net.add_edge(origem, destino, color="#C9C9C9", width=1, smooth={"type": "curvedCW", "roundness": 0.3}, arrows='false')

    arestas_reais = set()
    for i in range(len(lista_cameras) - 1):
        origem = lista_cameras[i]
        destino = lista_cameras[i + 1]
        if (origem, destino) in conexoes_validas or (destino, origem) in conexoes_validas:
            net.add_edge(origem, destino, color="yellow", width=3, smooth={"type": "curvedCW", "roundness": 0.3})
            arestas_reais.add((origem, destino))
            arestas_reais.add((destino, origem))

    caminho_probavel_completo = caminho_extra_inicio + lista_cameras + caminho_extra_fim
    for i in range(len(caminho_probavel_completo) - 1):
        origem = caminho_probavel_completo[i]
        destino = caminho_probavel_completo[i + 1]
        if ((origem, destino) in conexoes_validas or (destino, origem) in conexoes_validas) and \
                (origem, destino) not in arestas_reais and (destino, origem) not in arestas_reais:
            net.add_edge(origem, destino, color="#28C9FF", width=3, dashes=True, smooth={"type": "curvedCW", "roundness": 0.3})

    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")
    net.write_html(caminho_html, notebook=False)
    _injetar_legenda_no_html(caminho_html)
    return caminho_html


def carregar_conexoes_validas():
    caminho = os.path.join("Dados", "grafo.csv")
    conexoes = set()
    if os.path.exists(caminho):
        with open(caminho, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    origem = int(row['origem'])
                    destino = int(row['destino'])
                    conexoes.add((origem, destino))
                except:
                    continue
    return conexoes


def _injetar_legenda_no_html(caminho_html):
    if not os.path.exists(caminho_html):
        return

    with open(caminho_html, "r", encoding="utf-8") as f:
        conteudo = f.read()

    legenda_html = """<div style="position: absolute; top: 10px; left: 2px; background-color: #333; color: white; padding: 10px; font-size: 10px; border-radius: 0px 0px 10px 0px; z-index: 9999; font-family: Arial; box-shadow: 0 0 5px rgba(0,0,0,0.3);">
        <b>Legenda</b><br><br>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 3px; background-color: yellow; margin-right: 8px;"></div>
            <span> = Rota percorrida</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 3px; background-color: green; margin-right: 8px;"></div>
            <span> = Rota provável</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 12px; height: 12px; background-color: blue; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Entradas/Saídas próximas possíveis</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; background-color: red; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Câmera percorrida</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; background-color: green; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Câmera deduzida</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; background-color: orange; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Câmera pesquisada</span>
        </div>
    </div>"""

    if "</body>" in conteudo:
        conteudo = conteudo.replace("</body>", legenda_html + "\n</body>")
        with open(caminho_html, "w", encoding="utf-8") as f:
            f.write(conteudo)


if __name__ == "__main__":
    cameras_teste = [1, 3, 5, 6]
    gerar_grafo_por_hash(cameras_teste)
    print("Mapa gerado em: static/mapas/mapa.html")
