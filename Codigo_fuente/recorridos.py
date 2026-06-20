import networkx as nx
from collections import deque

def bfs_subgrafo(grafo, nodo_inicial, limite_nodos=150):
    visitados = set([nodo_inicial])
    cola = deque([nodo_inicial])
    aristas_bfs = []

    while cola and len(visitados) < limite_nodos:
        nodo = cola.popleft()
        for vecino in grafo.neighbors(nodo):
            if vecino not in visitados and len(visitados) < limite_nodos:
                visitados.add(vecino)
                cola.append(vecino)
                aristas_bfs.append((nodo, vecino))

    subgrafo_bfs = nx.Graph()
    subgrafo_bfs.add_nodes_from(visitados)
    subgrafo_bfs.add_edges_from(aristas_bfs)
    return subgrafo_bfs