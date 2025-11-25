class Graph:
    def __init__(self):
        # dicionário: bairro -> lista de (vizinho, peso)
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v, peso):
        """
        Adiciona aresta não-direcionada com peso.
        Se quiser um grafo direcionado, bastaria adicionar só um lado.
        """
        self.add_node(u)
        self.add_node(v)

        # evita duplicatas
        if not any(nei == v for nei, _ in self.adj[u]):
            self.adj[u].append((v, peso))

        if not any(nei == u for nei, _ in self.adj[v]):
            self.adj[v].append((u, peso))

    def neighbors(self, node):
        """Retorna lista de (vizinho, peso)"""
        return self.adj.get(node, [])

    def nodes(self):
        return list(self.adj.keys())

    def edges(self):
        """Retorna lista de arestas únicas (u, v, peso)"""
        e = set()
        for u in self.adj:
            for v, p in self.adj[u]:
                if (v, u, p) not in e:
                    e.add((u, v, p))
        return list(e)

    def degree(self, node):
        return len(self.adj.get(node, []))