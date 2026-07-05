import networkx as nx

class UFDS:
    def __init__(self, nodos):
        # al inicio cada nodo es su propio padre, todavia no hay grupos formados
        self.parent = {nodo: nodo for nodo in nodos}
        self.rank = {nodo: 0 for nodo in nodos}

    def find(self, i):
        if self.parent[i] == i:
            return i
        # aprovechamos para ir comprimiendo el camino y que las proximas busquedas sean mas rapidas
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            # unimos siempre el arbol mas chico debajo del mas grande para no desbalancear
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1

# aplica kruskal sobre el grafo y devuelve el mst junto con el peso total
def algoritmo_kruskal(grafo):
    aristas = []
    for u, v, datos in grafo.edges(data=True):
        peso = datos.get('weight', 1)
        aristas.append((peso, u, v))
    aristas.sort()  # necesitamos ir de menor a mayor peso para que kruskal funcione bien

    ufds = UFDS(list(grafo.nodes()))
    mst = nx.Graph()
    mst.add_nodes_from(grafo.nodes())

    peso_total = 0
    for peso, u, v in aristas:
        # si estan en distinto grupo, la arista no forma ciclo y la podemos agregar
        if ufds.find(u) != ufds.find(v):
            ufds.union(u, v)
            mst.add_edge(u, v, weight=peso)
            peso_total += peso

    return mst, peso_total