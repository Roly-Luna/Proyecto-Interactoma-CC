import networkx as nx

# Recorrido DFS (Depth First Search) usando LIFO (Pila/Stack)
def dfs_subgrafo(grafo, nodo_inicial, limite_nodos=150):
    visitados = set([nodo_inicial])
    pila = [nodo_inicial] # DFS usa pila, BFS usaba cola (deque)
    aristas_dfs = []

    while pila and len(visitados) < limite_nodos:
        nodo = pila.pop() # LIFO: Saca el ultimo agregado

        for vecino in grafo.neighbors(nodo):
            if vecino not in visitados and len(visitados) < limite_nodos:
                visitados.add(vecino)
                pila.append(vecino)
                aristas_dfs.append((nodo, vecino))

    subgrafo_dfs = nx.Graph()
    subgrafo_dfs.add_nodes_from(visitados)
    subgrafo_dfs.add_edges_from(aristas_dfs)

    return subgrafo_dfs