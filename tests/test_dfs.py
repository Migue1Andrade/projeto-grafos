import pytest
from src.graphs.algorithms import dfs

def test_dfs_ordem_sem_ciclo():
    graph = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['E'],
        'D': [],
        'E': []
    }

    ordem, ciclos = dfs(graph, 'A')

    assert ordem == ['A', 'B', 'D', 'C', 'E']

    assert ciclos == []


def test_dfs_detecta_ciclo():
    graph = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A'] 
    }

    ordem, ciclos = dfs(graph, 'A')

    assert ('C', 'A') in ciclos
    assert len(ciclos) >= 1
