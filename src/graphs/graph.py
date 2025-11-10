class Graph:
    def __init__(self):
        self.adjacency = {}

    def add_node(self, node):
        if node not in self.adjacency:
            self.adjacency[node] = []

    def add_edge(self, source, target, weight=1):
        self.add_node(source)
        self.add_node(target)
        self.adjacency[source].append((target, weight))

    def get(self, node, default=None):
        return self.adjacency.get(node, default if default is not None else [])

    def nodes(self):
        return list(self.adjacency.keys())

    def edges(self):
        edge_list = []
        for source, neighbors in self.adjacency.items():
            for target, weight in neighbors:
                edge_list.append((source, target, weight))
        return edge_list
