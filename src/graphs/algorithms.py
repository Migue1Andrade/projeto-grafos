from heapq import heappush, heappop

def _extract_neighbors(raw_neighbors):
    resultado = []

    for item in raw_neighbors:
        if isinstance(item, tuple):
            resultado.append(item[0])
        else:
            resultado.append(item)

    return resultado

def bfs(graph, start_node):
    visitados = set()
    fila = [start_node]
    ordem = []
    camadas = {start_node: 0}

    while fila:
        node = fila.pop(0)
        if node not in visitados:
            visitados.add(node)
            ordem.append(node)

            vizinhos = _extract_neighbors(graph.get(node, []))
            for viz in vizinhos:
                if viz not in visitados and viz not in fila:
                    camadas[viz] = camadas[node] + 1
                    fila.append(viz)

    return ordem, camadas

def dfs(graph, start_node):
    visitados = set()
    ordem = []
    pilha_rec = set()
    ciclos = []

    def explorar(node):
        visitados.add(node)
        pilha_rec.add(node)
        ordem.append(node)

        vizinhos = _extract_neighbors(graph.get(node, []))

        for viz in vizinhos:
            if viz not in visitados:
                explorar(viz)
            elif viz in pilha_rec:
                ciclos.append((node, viz))

        pilha_rec.remove(node)

    explorar(start_node)
    return ordem, ciclos

def dijkstra(grafo, origem):
    distancias = {no: float("inf") for no in grafo}
    distancias[origem] = 0

    heap = [(0, origem)]

    while heap:
        distancia_atual, u = heappop(heap)

        if distancia_atual > distancias[u]:
            continue

        for v, peso in grafo[u]:
            if peso < 0:
                raise ValueError("Dijkstra não suporta arestas com peso negativo")

            nova_distancia = distancia_atual + peso
            if nova_distancia < distancias[v]:
                distancias[v] = nova_distancia
                heappush(heap, (nova_distancia, v))

    return distancias

def bellman_ford(grafo, origem):
    distancias = {no: float("inf") for no in grafo}
    distancias[origem] = 0
    arestas = []

    for origem_no in grafo:
        for destino_no, peso in grafo[origem_no]:
            arestas.append((origem_no, destino_no, peso))

    for _ in range(len(grafo) - 1):
        mudou = False
        for origem_no, destino_no, peso in arestas:
            if distancias[origem_no] + peso < distancias[destino_no]:
                distancias[destino_no] = distancias[origem_no] + peso
                mudou = True
        if not mudou:
            break

    for origem_no, destino_no, peso in arestas:
        if distancias[origem_no] + peso < distancias[destino_no]:
            raise ValueError("Ciclo negativo detectado")

    return distancias
