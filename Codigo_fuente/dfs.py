import networkx as nx

# recorrido DFS usando una pila en vez de recursion, 
# asi evitamos problemas de limite de recursion con grafos grandes
def dfs_subgrafo(grafo, nodo_inicial, limite_nodos=150):
    visitados = set([nodo_inicial])
    pila = [nodo_inicial]
    aristas_dfs = []

    while pila and len(visitados) < limite_nodos:
        nodo = pila.pop()  # sacamos el ultimo que entro

        for vecino in grafo.neighbors(nodo):
            if vecino not in visitados and len(visitados) < limite_nodos:
                visitados.add(vecino)
                pila.append(vecino)
                aristas_dfs.append((nodo, vecino))

    subgrafo_dfs = nx.Graph()
    subgrafo_dfs.add_nodes_from(visitados)
    subgrafo_dfs.add_edges_from(aristas_dfs)

    return subgrafo_dfs