import csv
from src.graphs.io import load_bairros_csv, melt_bairros, save_csv
from src.graphs.graph import Graph

def construir_adjacencias(filepath_bairros: str, filepath_adjacencias: str):
    headers, rows = load_bairros_csv(filepath_bairros)
    bairros = melt_bairros(headers, rows)
    graph = Graph()
    # Adiciona adjacências por vizinhança na matriz
    for i, row in enumerate(rows):
        for j, bairro in enumerate(row):
            if bairro and bairro.strip():
                bairro_atual = bairro.strip()
                # Verifica vizinhos na matriz (horizontal e vertical)
                vizinhos = []
                # Horizontal
                if j > 0 and row[j-1] and row[j-1].strip():
                    vizinhos.append(row[j-1].strip())
                if j < len(row)-1 and row[j+1] and row[j+1].strip():
                    vizinhos.append(row[j+1].strip())
                # Vertical
                if i > 0 and rows[i-1][j] and rows[i-1][j].strip():
                    vizinhos.append(rows[i-1][j].strip())
                if i < len(rows)-1 and rows[i+1][j] and rows[i+1][j].strip():
                    vizinhos.append(rows[i+1][j].strip())
                for vizinho in vizinhos:
                    graph.add_edge(bairro_atual, vizinho)
    # Salva CSV de adjacências
    adjacencias = []
    for source in graph.nodes():
        for target, _ in graph.get(source):
            adjacencias.append([source, target])
    save_csv(filepath_adjacencias, adjacencias, header=["origem", "destino"])
    return graph

def construir_enderecos(bairros: list, filepath_enderecos: str):
    # Gera endereços fictícios para cada bairro
    enderecos = [[bairro, f"Rua Principal, 100 - {bairro}"] for bairro in bairros]
    save_csv(filepath_enderecos, enderecos, header=["bairro", "endereco"])
    return enderecos
