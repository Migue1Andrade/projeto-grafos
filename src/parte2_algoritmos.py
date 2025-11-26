import csv
import os
import time
import json
import collections
from collections import deque, defaultdict
from src.graphs.graph import Graph
from src.graphs.algorithms import bfs, dfs, dijkstra, bellman_ford

def carregar_grafo_voos(filepath):
    grafo = Graph()

    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)

        for row in reader:
            origem = row["Origem"].strip()
            destino = row["Destino"].strip()
            classe = row["Classe"].strip().lower()
            peso = float(row["Peso"])
            if classe == "economica":
                peso = -abs(peso)
            else:
                peso = abs(peso)
            grafo.add_edge(origem, destino, peso)

    return grafo

def gerar_info_dataset_voos(filepath_csv, out_path):
    vertices = set()
    arestas = 0
    graus = collections.defaultdict(int)
    pesos = set()

    with open(filepath_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)

        for row in reader:
            origem = row["Origem"].strip()
            destino = row["Destino"].strip()
            peso = float(row["Peso"])
            vertices.add(origem)
            vertices.add(destino)
            arestas += 1
            graus[origem] += 1
            pesos.add(peso)
    graus_lista = list(graus.values())
    info = {
        "num_vertices": len(vertices),
        "num_arestas": arestas,
        "tipo": "dirigido, ponderado",
        "grau_min": min(graus_lista) if graus_lista else 0,
        "grau_max": max(graus_lista) if graus_lista else 0,
        "grau_medio": sum(graus_lista)/len(graus_lista) if graus_lista else 0,
        "distribuicao_graus": dict(collections.Counter(graus_lista)),
        "exemplo_pesos": list(sorted(pesos))[:10],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"Info do dataset salva em {out_path}")

def rodar_bfs_dfs_graphs(g, fontes, out_dir):
    resultados = {}
    for fonte in fontes:
        # BFS
        t0 = time.time()
        ordem_bfs, camadas_bfs = bfs(g, fonte)
        t1 = time.time()
        resultados[f"BFS_{fonte}"] = {
            "ordem": ordem_bfs,
            "camadas": camadas_bfs,
            "tempo": t1-t0
        }
        # DFS
        t0 = time.time()
        ordem_dfs, ciclos_dfs = dfs(g, fonte)
        t1 = time.time()
        resultados[f"DFS_{fonte}"] = {
            "ordem": ordem_dfs,
            "ciclos": ciclos_dfs,
            "tempo": t1-t0
        }
    with open(os.path.join(out_dir, "bfs_dfs_resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return resultados

def rodar_dijkstra_graphs(g, pares, out_dir):
    resultados = {}
    for origem, destino in pares:
        t0 = time.time()
        distancias = dijkstra(g, origem)
        custo = distancias.get(destino, float('inf'))
        t1 = time.time()
        resultados[f"Dijkstra_{origem}_{destino}"] = {
            "custo": custo,
            "tempo": t1-t0
        }
    with open(os.path.join(out_dir, "dijkstra_resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return resultados

def rodar_bellman_ford_graphs(g, casos, out_dir):
    resultados = {}
    for origem, destino in casos:
        t0 = time.time()
        ciclo_negativo = False
        try:
            distancias = bellman_ford(g, origem)
            custo = distancias.get(destino, float('inf'))
        except Exception as e:
            custo = None
            ciclo_negativo = "ciclo negativo" in str(e).lower()
        t1 = time.time()
        resultados[f"BellmanFord_{origem}_{destino}"] = {
            "custo": custo,
            "ciclo_negativo": ciclo_negativo,
            "tempo": t1-t0
        }
    with open(os.path.join(out_dir, "bellman_ford_resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return resultados

def gerar_parte2_report(bfs_dfs, dijkstra_res, bellman_res, out_dir):
    tabela = []
    for k, v in bfs_dfs.items():
        tabela.append({"algoritmo": k, "tempo": v["tempo"], "info": v})
    for k, v in dijkstra_res.items():
        tabela.append({"algoritmo": k, "tempo": v["tempo"], "info": v})
    for k, v in bellman_res.items():
        tabela.append({"algoritmo": k, "tempo": v["tempo"], "info": v})

    with open(os.path.join(out_dir, "parte2_report.json"), "w", encoding="utf-8") as f:
        json.dump(tabela, f, ensure_ascii=False, indent=2)

def init_dataset_voos():
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    dataset_path = "data/dataset_parte2/adjacencias_voos.csv"
    gerar_info_dataset_voos(dataset_path, os.path.join(out_dir, "parte2_dataset_info.json"))

    g_dijkstra = defaultdict(list)
    g_bellman = defaultdict(list)

    with open(dataset_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            origem = row["Origem"].strip()
            destino = row["Destino"].strip()
            classe = row["Classe"].strip().lower()
            peso = float(row["Peso"])

            g_dijkstra[origem].append((destino, abs(peso)))

            if classe == "economica":
                peso_bf = -abs(peso)
            else:
                peso_bf = abs(peso)
            g_bellman[origem].append((destino, peso_bf))

    fontes = ["Mumbai", "Delhi", "Chennai"]
    bfs_dfs = rodar_bfs_dfs_graphs(g_dijkstra, fontes, out_dir)

    pares = [
        ("Mumbai", "Delhi"),
        ("Delhi", "Chennai"),
        ("Chennai", "Kolkata"),
        ("Kolkata", "Bangalore"),
        ("Bangalore", "Hyderabad"),
    ]
    dijkstra_res = rodar_dijkstra_graphs(g_dijkstra, pares, out_dir)

    casos_bf = [
        ("Mumbai", "Delhi"),
        ("Delhi", "Chennai"),
        ("Chennai", "Kolkata"),
        ("Kolkata", "Bangalore"),
        ("Bangalore", "Hyderabad"),
    ]
    bellman_res = rodar_bellman_ford_graphs(g_bellman, casos_bf, out_dir)

    gerar_parte2_report(bfs_dfs, dijkstra_res, bellman_res, out_dir)
    print("Pipeline parte 2 executada com sucesso!")

def main():
    init_dataset_voos()

if __name__ == "__main__":
    main()
