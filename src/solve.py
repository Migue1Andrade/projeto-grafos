import csv
import json
import os
import heapq
from math import inf

from src.graphs.io import (
    load_bairros_csv,
    save_csv,
    load_adjacencias,
)
from src.graphs.graph import Graph

from src.graphs.algorithms import dijkstra

def construir_grafo(filepath_adjacencias: str) -> Graph:
    adj_list = load_adjacencias(filepath_adjacencias)
    grafo = Graph()

    for origem, destino, logradouro, observacao, peso in adj_list:
        grafo.add_edge(origem, destino, peso)

    return grafo

def gerar_microrregioes_json(filepath_bairros):
    cebecas, linhas = load_bairros_csv(filepath_bairros)
    bairro_para_micro = {}

    for coluna_idx, cabeca in enumerate(cebecas):
        micro = cabeca.split(".")[0].strip()
        if not micro:
            continue

        for linha in linhas:
            if coluna_idx >= len(linha):
                continue
            celula = linha[coluna_idx]
            if not celula:
                continue
            bairro = celula.strip()
            if not bairro:
                continue

            bairro_para_micro[bairro] = micro

    return bairro_para_micro

def gerar_bairros_unique_csv(
    bairro_para_micro: dict, filepath: str = "data/bairros_unique.csv"
):

    linhas = [
        [bairro, microrregiao]
        for (bairro, microrregiao) in sorted(
            bairro_para_micro.items(),
            key=lambda x: (int(x[1]), x[0]),
        )
    ]
    save_csv(filepath, linhas, header=["bairro", "microrregiao"])

def agrupar_nos_microrregioes(grafo: Graph, bairro_para_micro: dict):
    micros = {}
    for bairro in grafo.nodes():
        microrregiao = bairro_para_micro.get(bairro)
        if not microrregiao:
            continue
        micros.setdefault(microrregiao, set()).add(bairro)

    edges = grafo.edges()
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

def calcular_metricas_globais(grafo: Graph) -> dict:
    num_nos = len(grafo.nodes())
    num_arestas = len(grafo.edges())

    if num_nos <= 1:
        densidade = 0.0
    else:
        densidade = (2 * num_arestas) / (num_nos * (num_nos - 1))

    return {
        "ordem": num_nos,
        "tamanho": num_arestas,
        "densidade": densidade,
    }

def dijkstra_caminho(grafo: Graph, origem: str, destino: str):
    distancias = {no: inf for no in grafo.nodes()}
    anteriores = {no: None for no in grafo.nodes()}
    distancias[origem] = 0.0

    heap = [(0.0, origem)]

    while heap:
        custo_atual, no_atual = heapq.heappop(heap)

        if no_atual == destino:
            break

        if custo_atual > distancias[no_atual]:
            continue

        for vizinho, peso in grafo.neighbors(no_atual):
            novo_custo = custo_atual + peso
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                anteriores[vizinho] = no_atual
                heapq.heappush(heap, (novo_custo, vizinho))

    if distancias[destino] == inf:
        return inf, []

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]
    caminho.reverse()

    return distancias[destino], caminho

def calcular_graus(grafo: Graph):
    graus = [(bairro, grafo.degree(bairro)) for bairro in grafo.nodes()]
    graus.sort(key=lambda x: (-x[1], x[0]))

    return graus

def calcular_ego(grafo: Graph):
    ego_info = []
    todas_arestas = grafo.edges()

    for bairro in grafo.nodes():
        vizinhos = [vizinho for (vizinho, _) in grafo.neighbors(bairro)]
        grau = len(vizinhos)

        nos_ego = set([bairro] + vizinhos)
        ordem_ego = len(nos_ego)

        tamanho_ego = 0
        for origem, destino, _ in todas_arestas:
            if origem in nos_ego and destino in nos_ego:
                tamanho_ego += 1

        if ordem_ego <= 1:
            densidade_ego = 0.0
        else:
            densidade_ego = (2 * tamanho_ego) / (ordem_ego * (ordem_ego - 1))

        ego_info.append((bairro, grau, ordem_ego, tamanho_ego, densidade_ego))

    ego_info.sort(key=lambda x: x[0])

    return ego_info

def normalizar_bairro_destino(bairro: str) -> str:
    if not bairro:
        return bairro

    nome = bairro.strip()

    if "setúbal" in nome.lower():
        return "Boa Viagem"

    return nome

def calcular_distancias_enderecos(g: Graph, filepath_enderecos: str = "data/enderecos.csv"):
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

            if bairro_X.lower() == "nova descoberta" and "setúbal" in bairro_Y_original.lower():
                percurso_nd_setubal = {
                    "origem": bairro_X,
                    "destino_informado": bairro_Y_original,
                    "destino_no_grafo": bairro_Y,
                    "custo": custo,
                    "caminho": caminho,
                }

    return linhas_saida, percurso_nd_setubal

def criar_arquivo_json(caminho, dado):
    with open(os.path.join("out", caminho), "w", encoding="utf-8") as f:
        json.dump(dado, f, ensure_ascii=False, indent=2)

#Func que inicia todos os out para manipulação
def init():
    try:
        bairros_microrregioes = gerar_microrregioes_json("data/bairros_recife.csv")

        gerar_bairros_unique_csv(bairros_microrregioes, "data/bairros_unique.csv")

        grafo = construir_grafo("data/adjacencias_bairros.csv")
        metricas = calcular_metricas_globais(grafo)
        microrregioes = agrupar_nos_microrregioes(grafo, bairros_microrregioes)
        graus = calcular_graus(grafo)
        ego = calcular_ego(grafo)
        ranking = calcular_ranking(graus, ego)
        linhas_graus = [[bairro, grau] for (bairro, grau) in graus]
        linhas_ego = [
            [bairro, grau, ordem_ego, tamanho_ego, dens_ego]
            for (bairro, grau, ordem_ego, tamanho_ego, dens_ego) in ego
        ]

        # Garante out/
        os.makedirs("out", exist_ok=True)

        criar_arquivo_json("recife_global.json", metricas)
        criar_arquivo_json("microrregioes.json", microrregioes)
        save_csv(os.path.join("out", "graus.csv"), linhas_graus, header=["bairro", "grau"])
        save_csv(
            os.path.join("out", "ego_bairro.csv"),
            linhas_ego,
            header=["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"],
        )
        criar_arquivo_json("ranking_bairros.json", ranking)
        gerar_distancias_enderecos("data/enderecos.csv", "out", grafo)
    except Exception as e:
        print(f"Erro ao inicializar os arquivos de saída: {e}")

def gerar_distancias_enderecos(filepath_enderecos: str, out_dir: str, grafo: Graph):
    linhas, percurso_nd_setubal = calcular_distancias_enderecos(grafo, filepath_enderecos)

    save_csv(
        os.path.join(out_dir, "distancias_enderecos.csv"),
        linhas,
        header=["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"],
    )

    if percurso_nd_setubal is not None:
        criar_arquivo_json("percurso_nova_descoberta_setubal.json", percurso_nd_setubal )

def calcular_ranking(graus, ego):
    bairro_grau, valor_grau = max(graus, key=lambda x: x[1])
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
