import networkx as nx

class UFDS:
    def __init__(self, nodos):
        # Inicializa cada nodo como su propio padre (diccionarios para manejar IDs de proteinas)
        self.parent = {nodo: nodo for nodo in nodos}
        self.rank = {nodo: 0 for nodo in nodos}

    def find(self, i):
        if self.parent[i] == i:
            return i
        # Compresion de caminos
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            # Union por rango
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
                
# Aplica Kruskal sobre un grafo para retornar su MST (Arbol de Expansion Minima).
def algoritmo_kruskal(grafo):
    # 1. Extraer y ordenar aristas por peso
    aristas = []
    for u, v, datos in grafo.edges(data=True):
        peso = datos.get('weight', 1)
        aristas.append((peso, u, v))
    aristas.sort() # Orden de menor a mayor peso

    # 2. Inicializar UFDS
    ufds = UFDS(list(grafo.nodes()))
    mst = nx.Graph()
    mst.add_nodes_from(grafo.nodes())

    # 3. Construir el MST
    peso_total = 0
    for peso, u, v in aristas:
        if ufds.find(u) != ufds.find(v):
            ufds.union(u, v)
            mst.add_edge(u, v, weight=peso)
            peso_total += peso

    return mst, peso_total