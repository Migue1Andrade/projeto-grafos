import os
import json
import csv

from pyvis.network import Network
import matplotlib.pyplot as plt

from src.solve import construir_grafo
from src.graphs.io import load_adjacencias


# -------------------------------------------------------------------
# Utilitários
# -------------------------------------------------------------------


def _carregar_percurso(percurso_json_path: str):
    """
    Lê o JSON gerado em out/percurso_nova_descoberta_setubal.json
    e devolve a lista de bairros no caminho.
    """
    with open(percurso_json_path, encoding="utf-8") as f:
        data = json.load(f)
    caminho = data.get("caminho", [])
    return caminho, data


def _carregar_ego(ego_csv_path: str):
    """
    Lê out/ego_bairro.csv -> dict[bairro] = {grau, ordem_ego, tamanho_ego, densidade_ego}
    """
    stats = {}
    if not os.path.exists(ego_csv_path):
        return stats

    with open(ego_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bairro = row["bairro"]
            stats[bairro] = {
                "grau": float(row["grau"]),
                "ordem_ego": float(row["ordem_ego"]),
                "tamanho_ego": float(row["tamanho_ego"]),
                "densidade_ego": float(row["densidade_ego"]),
            }
    return stats


def _carregar_microrregioes(bairros_unique_path: str):
    """
    Lê data/bairros_unique.csv -> dict[bairro] = microrregiao
    """
    mapping = {}
    if not os.path.exists(bairros_unique_path):
        return mapping

    with open(bairros_unique_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["bairro"]] = row["microrregiao"]
    return mapping


def _carregar_ranking(ranking_path: str):
    """
    Lê out/ranking_bairros.json
    """
    if not os.path.exists(ranking_path):
        return {}
    with open(ranking_path, encoding="utf-8") as f:
        return json.load(f)


def _carregar_distancias(distancias_csv_path: str):
    """
    Lê out/distancias_enderecos.csv (opcional).
    Usaremos depois para o modo 'Waze', então aqui só deixo preparado.
    """
    dados = []
    if not os.path.exists(distancias_csv_path):
        return dados

    with open(distancias_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dados.append(row)
    return dados


# Paleta simples por microrregião (1..6)
MICRO_CORES = {
    "1": "#1E88E5",  # azul
    "2": "#43A047",  # verde
    "3": "#FB8C00",  # laranja
    "4": "#8E24AA",  # roxo
    "5": "#F4511E",  # vermelho
    "6": "#00897B",  # teal
}


# -------------------------------------------------------------------
# 7) Árvore do percurso – versão premium simples
# -------------------------------------------------------------------


def gerar_arvore_percurso_premium(
    percurso_json_path: str = "out/percurso_nova_descoberta_setubal.json",
    out_html_path: str = "out/arvore_percurso.html",
):
    """
    Gera uma visualização mais bonita da árvore/caminho
    Nova Descoberta -> Boa Viagem (Setúbal) usando PyVis.
    """

    if not os.path.exists(percurso_json_path):
        raise FileNotFoundError(
            f"Arquivo de percurso não encontrado: {percurso_json_path}"
        )

    caminho, data = _carregar_percurso(percurso_json_path)

    if not caminho:
        raise ValueError("Caminho vazio no JSON de percurso.")

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
    )

    net.barnes_hut()

    origem = caminho[0]
    destino = caminho[-1]

    for bairro in caminho:
        if bairro == origem:
            color = "#43A047"  # origem em verde
            size = 26
        elif bairro == destino:
            color = "#F4511E"  # destino em vermelho
            size = 26
        else:
            color = "#1E88E5"
            size = 18

        net.add_node(
            bairro,
            label=bairro,
            color=color,
            size=size,
            title=bairro,
        )

    # arestas sequenciais
    for i in range(len(caminho) - 1):
        u = caminho[i]
        v = caminho[i + 1]
        net.add_edge(
            u,
            v,
            color="#EF6C00",
            width=4,
            smooth={"type": "continuous", "roundness": 0.5},
        )

    # Opções em JSON VÁLIDO
    net.set_options(
        '''
{
  "interaction": {
    "hover": true,
    "zoomView": true,
    "dragView": true,
    "navigationButtons": true
  },
  "nodes": {
    "shape": "dot",
    "borderWidth": 1,
    "borderWidthSelected": 3,
    "shadow": true,
    "font": {
      "size": 18,
      "face": "arial"
    }
  },
  "edges": {
    "smooth": {
      "type": "continuous",
      "roundness": 0.6
    }
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "springLength": 180,
      "springConstant": 0.02,
      "damping": 0.09
    }
  }
}
        '''
    )

    os.makedirs(os.path.dirname(out_html_path), exist_ok=True)
    net.write_html(out_html_path)
    print(out_html_path)


# -------------------------------------------------------------------
# 9) Grafo interativo premium simples
# -------------------------------------------------------------------


def gerar_grafo_interativo_premium(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    bairros_unique_path: str = "data/bairros_unique.csv",
    ego_csv_path: str = "out/ego_bairro.csv",
    ranking_path: str = "out/ranking_bairros.json",
    percurso_json_path: str = "out/percurso_nova_descoberta_setubal.json",
    out_html_path: str = "out/grafo_interativo.html",
):
    """
    Gera o grafo interativo principal com:
      - cores por microrregião
      - tamanho do nó proporcional ao grau
      - tooltip com grau + microrregião + densidade_ego
      - caminho Nova Descoberta -> Boa Viagem (Setúbal) destacado
    """

    # Carrega grafo
    g = construir_grafo(filepath_adjacencias)

    # Estatísticas auxiliares
    ego_stats = _carregar_ego(ego_csv_path)
    micro_map = _carregar_microrregioes(bairros_unique_path)
    ranking = _carregar_ranking(ranking_path)

    maior_grau = ranking.get("maior_grau", {})
    maior_denso = ranking.get("maior_densidade_ego", {})

    bairro_top_grau = maior_grau.get("bairro")
    bairro_top_denso = maior_denso.get("bairro")

    # Caminho especial
    caminho_destacado = []
    if os.path.exists(percurso_json_path):
        caminho_destacado, _ = _carregar_percurso(percurso_json_path)

    arestas_caminho = set()
    if caminho_destacado:
        for i in range(len(caminho_destacado) - 1):
            u = caminho_destacado[i]
            v = caminho_destacado[i + 1]
            arestas_caminho.add((u, v))
            arestas_caminho.add((v, u))

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
    )

    net.barnes_hut()

    # Nós
    for bairro in g.nodes():
        info_ego = ego_stats.get(bairro, {})
        grau = info_ego.get("grau", float(len(g.neighbors(bairro))))
        dens_ego = info_ego.get("densidade_ego", 0.0)
        microrregiao = micro_map.get(bairro, "?")

        # Tamanho baseado no grau (com limites)
        size = 8 + min(max(grau, 1), 12) * 1.3

        # Cor pela microrregião
        color = MICRO_CORES.get(str(microrregiao), "#90A4AE")

        # Destaques especiais
        border_width = 1
        if bairro == bairro_top_grau or bairro == bairro_top_denso:
            border_width = 3
            size += 4
            color = "#FDD835"  # amarelo destaque

        title = (
            f"<b>{bairro}</b><br>"
            f"Microrregião: {microrregiao}<br>"
            f"Grau: {grau:.0f}<br>"
            f"Densidade ego: {dens_ego:.3f}"
        )

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color=color,
            size=size,
            borderWidth=border_width,
        )

    # Arestas
    for u, v, peso in g.edges():
        # Are we in the highlighted path?
        if (u, v) in arestas_caminho:
            color = "#E53935"
            width = 3
        else:
            color = "#CFD8DC"
            width = 1

        net.add_edge(u, v, color=color, width=width, title=f"peso: {peso}")

    net.set_options(
        '''
{
  "interaction": {
    "hover": true,
    "zoomView": true,
    "dragView": true,
    "navigationButtons": true
  },
  "nodes": {
    "shape": "dot",
    "borderWidth": 1,
    "borderWidthSelected": 3,
    "shadow": true,
    "font": {
      "size": 16,
      "face": "arial"
    }
  },
  "edges": {
    "color": {
      "inherit": false
    },
    "smooth": {
      "type": "continuous",
      "roundness": 0.4
    }
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -12000,
      "springLength": 160,
      "springConstant": 0.04,
      "damping": 0.09
    }
  }
}
        '''
    )

    os.makedirs(os.path.dirname(out_html_path), exist_ok=True)
    net.write_html(out_html_path)
    print(out_html_path)


# -------------------------------------------------------------------
# 8) Visualizações analíticas básicas (já fizemos, mas deixo aqui)
# -------------------------------------------------------------------


def plot_histograma_graus(
    graus_csv_path: str = "out/graus.csv",
    out_path: str = "out/histograma_graus.png",
):
    if not os.path.exists(graus_csv_path):
        return

    graus = []
    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            graus.append(int(row["grau"]))

    plt.figure(figsize=(8, 5))
    plt.hist(graus, bins=10)
    plt.xlabel("Grau")
    plt.ylabel("Frequência")
    plt.title("Distribuição dos graus dos bairros")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_top10_grau(
    graus_csv_path: str = "out/graus.csv",
    out_path: str = "out/top10_grau.png",
):
    if not os.path.exists(graus_csv_path):
        return

    dados = []
    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dados.append((row["bairro"], int(row["grau"])))

    dados.sort(key=lambda x: x[1], reverse=True)
    top10 = dados[:10]

    labels = [x[0] for x in top10]
    valores = [x[1] for x in top10]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, valores)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Grau")
    plt.title("Top 10 bairros por grau")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def gerar_subgrafo_top10_grau_html(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    graus_csv_path: str = "out/graus.csv",
    out_html_path: str = "out/subgrafo_top10_grau.html",
):
    if not os.path.exists(graus_csv_path):
        return

    # carrega grafo completo
    g = construir_grafo(filepath_adjacencias)

    # pega top10
    dados = []
    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dados.append((row["bairro"], int(row["grau"])))
    dados.sort(key=lambda x: x[1], reverse=True)
    top10_bairros = {b for b, _ in dados[:10]}

    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="#222222")

    net.barnes_hut()

    for bairro in g.nodes():
        if bairro in top10_bairros:
            net.add_node(
                bairro,
                label=bairro,
                color="#1E88E5",
                size=22,
                title=f"Top 10 por grau",
            )

    for u, v, peso in g.edges():
        if u in top10_bairros and v in top10_bairros:
            net.add_edge(u, v, color="#90CAF9", width=2, title=f"peso: {peso}")

    net.set_options(
        '''
{
  "interaction": {
    "hover": true,
    "zoomView": true,
    "dragView": true,
    "navigationButtons": true
  },
  "nodes": {
    "shape": "dot",
    "shadow": true,
    "font": {
      "size": 18,
      "face": "arial"
    }
  },
  "edges": {
    "smooth": {
      "type": "continuous",
      "roundness": 0.4
    }
  },
  "physics": {
    "enabled": true
  }
}
        '''
    )

    os.makedirs(os.path.dirname(out_html_path), exist_ok=True)
    net.write_html(out_html_path)
    print(out_html_path)


def gerar_visualizacoes_analiticas_basicas():
    """
    Gera:
      - out/histograma_graus.png
      - out/top10_grau.png
      - out/subgrafo_top10_grau.html
    """
    plot_histograma_graus()
    plot_top10_grau()
    gerar_subgrafo_top10_grau_html()


# -------------------------------------------------------------------
# Função geral para rodar tudo da parte de visualização
# -------------------------------------------------------------------


def gerar_visualizacoes_premium():
    """
    Roda tudo da parte 7, 8 e 9:
      - árvore do percurso (HTML)
      - grafo interativo premium (HTML)
      - visualizações analíticas básicas (PNG + HTML)
    """
    gerar_arvore_percurso_premium()
    gerar_grafo_interativo_premium()
    gerar_visualizacoes_analiticas_basicas()