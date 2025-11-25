import csv
import json
import os
import heapq
from math import inf

from src.graphs.io import (
    load_bairros_csv,
    melt_bairros,
    save_csv,
    load_adjacencias,
)
from src.graphs.graph import Graph

from src.graphs.algorithms import dijkstra

# ----------------------------------------------------------------------
# (Mantido por compatibilidade, mas não usado no fluxo atual)
# ----------------------------------------------------------------------
def construir_adjacencias(filepath_bairros: str, filepath_adjacencias: str):
    headers, rows = load_bairros_csv(filepath_bairros)
    bairros = melt_bairros(headers, rows)
    graph = Graph()

    # Versão simples com peso 1.0 só pela estrutura
    for i, row in enumerate(rows):
        for j, bairro in enumerate(row):
            if bairro and bairro.strip():
                bairro_atual = bairro.strip()
                vizinhos = []

                # Horizontal
                if j > 0 and row[j - 1] and row[j - 1].strip():
                    vizinhos.append(row[j - 1].strip())
                if j < len(row) - 1 and row[j + 1] and row[j + 1].strip():
                    vizinhos.append(row[j + 1].strip())

                # Vertical
                if i > 0 and rows[i - 1][j] and rows[i - 1][j].strip():
                    vizinhos.append(rows[i - 1][j].strip())
                if i < len(rows) - 1 and rows[i + 1][j] and rows[i + 1][j].strip():
                    vizinhos.append(rows[i + 1][j].strip())

                for vizinho in vizinhos:
                    graph.add_edge(bairro_atual, vizinho, 1.0)

    adjacencias = []
    for u, v, p in graph.edges():
        adjacencias.append([u, v, p])

    save_csv(filepath_adjacencias, adjacencias, header=["origem", "destino", "peso"])
    return graph


def construir_enderecos(bairros: list, filepath_enderecos: str):
    enderecos = [[bairro, f"Rua Principal, 100 - {bairro}"] for bairro in bairros]
    save_csv(filepath_enderecos, enderecos, header=["bairro", "endereco"])
    return enderecos


# ----------------------------------------------------------------------
# Grafo principal
# ----------------------------------------------------------------------
def construir_grafo(filepath_adjacencias: str) -> Graph:
    adj_list = load_adjacencias(filepath_adjacencias)
    g = Graph()

    for origem, destino, logradouro, observacao, peso in adj_list:
        g.add_edge(origem, destino, peso)

    return g


# ----------------------------------------------------------------------
# Microrregiões (bairros_unique + métricas de subgrafos)
# ----------------------------------------------------------------------
def carregar_microrregioes(filepath_bairros: str = "data/bairros_recife.csv"):
    """
    Lê o CSV de bairros em matriz (1.1..6.3) e devolve:
      - dict bairro -> microrregiao (string: '1', '2', ..., '6')
    """
    headers, rows = load_bairros_csv(filepath_bairros)
    bairro_para_micro = {}

    for col_idx, header in enumerate(headers):
        # Ex.: '1.1' -> '1'
        micro = header.split(".")[0].strip()
        if not micro:
            continue

        for row in rows:
            if col_idx >= len(row):
                continue
            cell = row[col_idx]
            if not cell:
                continue
            bairro = cell.strip()
            if not bairro:
                continue

            # Se um bairro aparecer duas vezes, a última sobrescreve;
            # na prática, no dataset isso não deve acontecer.
            bairro_para_micro[bairro] = micro

    return bairro_para_micro


def gerar_bairros_unique(
    bairro_para_micro: dict, filepath: str = "data/bairros_unique.csv"
):
    """
    Gera o arquivo bairros_unique.csv no formato:
      bairro, microrregiao
    """
    linhas = [
        [bairro, microrregiao]
        for (bairro, microrregiao) in sorted(
            bairro_para_micro.items(),
            key=lambda x: (int(x[1]), x[0]),
        )
    ]
    save_csv(filepath, linhas, header=["bairro", "microrregiao"])


def calcular_microrregioes(g: Graph, bairro_para_micro: dict):
    """
    Para cada microrregião (1..6), calcula:
      - ordem (número de bairros do grupo que aparecem no grafo)
      - tamanho (número de arestas internas ao grupo)
      - densidade
    Retorna lista de dicionários:
      { microrregiao, ordem, tamanho, densidade }
    """
    # Agrupa nós por microrregião
    micros = {}
    for bairro in g.nodes():
        microrregiao = bairro_para_micro.get(bairro)
        if not microrregiao:
            continue
        micros.setdefault(microrregiao, set()).add(bairro)

    # Lista única de arestas
    edges = g.edges()
    resultados = []

    for microrregiao, nodes_set in sorted(micros.items(), key=lambda x: int(x[0])):
        n = len(nodes_set)
        m = 0

        for u, v, _ in edges:
            if u in nodes_set and v in nodes_set:
                m += 1

        if n <= 1:
            densidade = 0.0
        else:
            densidade = (2 * m) / (n * (n - 1))

        resultados.append(
            {
                "microrregiao": microrregiao,
                "ordem": n,
                "tamanho": m,
                "densidade": densidade,
            }
        )

    return resultados


# ----------------------------------------------------------------------
# Métricas globais, graus e ego-subrede
# ----------------------------------------------------------------------
def calcular_metricas_globais(g: Graph) -> dict:
    n = len(g.nodes())
    m = len(g.edges())

    if n <= 1:
        densidade = 0.0
    else:
        densidade = (2 * m) / (n * (n - 1))

    return {
        "ordem": n,
        "tamanho": m,
        "densidade": densidade,
    }

def dijkstra_caminho(g: Graph, origem: str, destino: str):
    """
    Versão de Dijkstra que retorna custo e caminho explícito
    no grafo de bairros.
    """
    dist = {n: inf for n in g.nodes()}
    prev = {n: None for n in g.nodes()}
    dist[origem] = 0.0

    heap = [(0.0, origem)]

    while heap:
        custo_atual, u = heapq.heappop(heap)

        if u == destino:
            break

        if custo_atual > dist[u]:
            continue

        for v, peso in g.neighbors(u):
            novo = custo_atual + peso
            if novo < dist[v]:
                dist[v] = novo
                prev[v] = u
                heapq.heappush(heap, (novo, v))

    # Reconstrói caminho
    if dist[destino] == inf:
        return inf, []

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = prev[atual]
    caminho.reverse()

    return dist[destino], caminho

def calcular_graus(g: Graph):
    graus = [(bairro, g.degree(bairro)) for bairro in g.nodes()]
    graus.sort(key=lambda x: (-x[1], x[0]))
    return graus


def calcular_ego(g: Graph):
    ego_info = []
    edges = g.edges()

    for bairro in g.nodes():
        vizinhos = [v for (v, _) in g.neighbors(bairro)]
        grau = len(vizinhos)

        ego_nodes = set([bairro] + vizinhos)
        ordem_ego = len(ego_nodes)

        tamanho_ego = 0
        for u, v, _ in edges:
            if u in ego_nodes and v in ego_nodes:
                tamanho_ego += 1

        if ordem_ego <= 1:
            dens_ego = 0.0
        else:
            dens_ego = (2 * tamanho_ego) / (ordem_ego * (ordem_ego - 1))

        ego_info.append((bairro, grau, ordem_ego, tamanho_ego, dens_ego))

    ego_info.sort(key=lambda x: x[0])
    return ego_info

def normalizar_bairro_destino(bairro: str) -> str:
    """
    Trata casos especiais, como Setúbal -> Boa Viagem.
    """
    if not bairro:
        return bairro

    nome = bairro.strip()

    # Caso específico da proposta: Setúbal é sub-bairro de Boa Viagem
    if "setúbal" in nome.lower():
        return "Boa Viagem"

    return nome


def calcular_distancias_enderecos(g: Graph, filepath_enderecos: str = "data/enderecos.csv"):
    """
    Lê data/enderecos.csv e calcula custo/caminho entre os bairros
    usando Dijkstra.
    Retorna:
      - lista com linhas para distancias_enderecos.csv
      - dado especial do percurso Nova Descoberta -> Setúbal/Boa Viagem
    """
    linhas_saida = []
    percurso_nd_setubal = None

    with open(filepath_enderecos, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            X = row["X"]
            Y = row["Y"]
            bairro_X = row["bairro_X"].strip()
            bairro_Y_original = row["bairro_Y"].strip()
            bairro_Y = normalizar_bairro_destino(bairro_Y_original)

            # Calcula no grafo usando Dijkstra com caminho
            custo, caminho = dijkstra_caminho(g, bairro_X, bairro_Y)
            caminho_str = " -> ".join(caminho) if caminho else ""

            linhas_saida.append([
                X,
                Y,
                bairro_X,
                bairro_Y_original,
                custo,
                caminho_str,
            ])

            # Guarda percurso especial Nova Descoberta -> Setúbal/Boa Viagem
            if bairro_X.lower() == "nova descoberta" and "setúbal" in bairro_Y_original.lower():
                percurso_nd_setubal = {
                    "origem": bairro_X,
                    "destino_informado": bairro_Y_original,
                    "destino_no_grafo": bairro_Y,
                    "custo": custo,
                    "caminho": caminho,
                }

    return linhas_saida, percurso_nd_setubal

# ----------------------------------------------------------------------
# Função principal da Parte 1
# ----------------------------------------------------------------------
def gerar_arquivos_entrega1(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    filepath_bairros: str = "data/bairros_recife.csv",
    out_dir: str = "out",
):
    """
    Parte 1 – Gera:
      - data/bairros_unique.csv
      - out/recife_global.json
      - out/microrregioes.json
      - out/graus.csv
      - out/ego_bairro.csv
    """
    # 0) Carrega mapeamento bairro -> microrregiao e gera bairros_unique.csv
    bairro_para_micro = carregar_microrregioes(filepath_bairros)
    gerar_bairros_unique(bairro_para_micro, "data/bairros_unique.csv")

    # 1) Constrói grafo principal a partir das adjacências
    g = construir_grafo(filepath_adjacencias)

    # 2) Métricas globais
    metricas = calcular_metricas_globais(g)

    # 3) Microrregiões (subgrafos)
    microrregioes = calcular_microrregioes(g, bairro_para_micro)

    # 4) Graus
    graus = calcular_graus(g)

    # 5) Ego-subrede
    ego = calcular_ego(g)

    # 6) Ranking dos bairros
    ranking = calcular_ranking(graus, ego)

    # Garante out/
    os.makedirs(out_dir, exist_ok=True)

    # Salva JSON global
    with open(os.path.join(out_dir, "recife_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)

    # Salva microrregioes.json
    with open(
        os.path.join(out_dir, "microrregioes.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(microrregioes, f, ensure_ascii=False, indent=2)

    # Salva graus.csv
    linhas_graus = [[bairro, grau] for (bairro, grau) in graus]
    save_csv(os.path.join(out_dir, "graus.csv"), linhas_graus, header=["bairro", "grau"])

    # Salva ego_bairro.csv
    linhas_ego = [
        [bairro, grau, ordem_ego, tamanho_ego, dens_ego]
        for (bairro, grau, ordem_ego, tamanho_ego, dens_ego) in ego
    ]
    save_csv(
        os.path.join(out_dir, "ego_bairro.csv"),
        linhas_ego,
        header=["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"],
    )
    
    # Salva ranking_bairros.json
    with open(os.path.join(out_dir, "ranking_bairros.json"), "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)
    
    return metricas, microrregioes, graus, ego, ranking

def gerar_distancias_enderecos(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    filepath_enderecos: str = "data/enderecos.csv",
    out_dir: str = "out",
):
    """
    Gera:
      - out/distancias_enderecos.csv
      - out/percurso_nova_descoberta_setubal.json
    """
    g = construir_grafo(filepath_adjacencias)

    linhas, percurso_nd_setubal = calcular_distancias_enderecos(g, filepath_enderecos)

    os.makedirs(out_dir, exist_ok=True)

    # CSV com todas as distâncias
    save_csv(
        os.path.join(out_dir, "distancias_enderecos.csv"),
        linhas,
        header=["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"],
    )

    # JSON específico do percurso Nova Descoberta -> Setúbal
    if percurso_nd_setubal is not None:
        with open(
            os.path.join(out_dir, "percurso_nova_descoberta_setubal.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(percurso_nd_setubal, f, ensure_ascii=False, indent=2)

    return linhas, percurso_nd_setubal


def calcular_ranking(graus, ego):
    """
    Recebe:
      - graus: lista de (bairro, grau)
      - ego:   lista de (bairro, grau, ordem_ego, tamanho_ego, densidade_ego)

    Retorna um dicionário com:
      - bairro de maior grau
      - bairro de maior densidade_ego
    """
    # Bairro com maior grau
    bairro_grau, valor_grau = max(graus, key=lambda x: x[1])

    # Bairro com maior densidade de ego-subrede
    bairro_ego = max(ego, key=lambda x: x[4])
    bairro_denso = bairro_ego[0]
    grau_denso = bairro_ego[1]
    ordem_ego = bairro_ego[2]
    tamanho_ego = bairro_ego[3]
    densidade_ego = bairro_ego[4]

    ranking = {
        "maior_grau": {
            "bairro": bairro_grau,
            "grau": valor_grau,
        },
        "maior_densidade_ego": {
            "bairro": bairro_denso,
            "grau": grau_denso,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": densidade_ego,
        },
    }

    return ranking

def carregar_enderecos(filepath: str):
    pares = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            X = row["X"]
            Y = row["Y"]
            bX = row["bairro_X"].strip()
            bY = row["bairro_Y"].strip()
            pares.append((X, Y, bX, bY))
    return pares