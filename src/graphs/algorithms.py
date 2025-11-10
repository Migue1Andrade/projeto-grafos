from collections import deque
import heapq

def bfs(graph, start_node):
    visited_nodes = set()
    node_queue = deque([start_node])
    traversal_order = []

    while node_queue:
        current_node = node_queue.popleft()
        if current_node not in visited_nodes:
            visited_nodes.add(current_node)
            traversal_order.append(current_node)
            node_queue.extend(
                neighbor for neighbor in graph.get(current_node, []) if neighbor not in visited_nodes
            )

    return traversal_order

def dfs(graph, start_node):
    visited_nodes = set()
    node_stack = [start_node]
    traversal_order = []

    while node_stack:
        current_node = node_stack.pop()
        if current_node not in visited_nodes:
            visited_nodes.add(current_node)
            traversal_order.append(current_node)
            node_stack.extend(
                neighbor for neighbor in reversed(graph.get(current_node, [])) if neighbor not in visited_nodes
            )

    return traversal_order

def dijkstra(graph, start_node):
    shortest_distances = {node: float('inf') for node in graph}
    shortest_distances[start_node] = 0
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance > shortest_distances[current_node]:
            continue

        for neighbor, edge_weight in graph.get(current_node, []):
            new_distance = current_distance + edge_weight
            if new_distance < shortest_distances[neighbor]:
                shortest_distances[neighbor] = new_distance
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return shortest_distances

def bellman_ford(graph, start_node):
    shortest_distances = {node: float('inf') for node in graph}
    shortest_distances[start_node] = 0
    edge_list = []

    for source_node in graph:
        for destination_node, edge_weight in graph[source_node]:
            edge_list.append((source_node, destination_node, edge_weight))

    for _ in range(len(graph) - 1):
        for source_node, destination_node, edge_weight in edge_list:
            if shortest_distances[source_node] + edge_weight < shortest_distances[destination_node]:
                shortest_distances[destination_node] = shortest_distances[source_node] + edge_weight

    for source_node, destination_node, edge_weight in edge_list:
        if shortest_distances[source_node] + edge_weight < shortest_distances[destination_node]:
            raise ValueError("Graph contains a negative-weight cycle")

    return shortest_distances
