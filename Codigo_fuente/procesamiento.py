import pandas as pd
import networkx as nx

# Carga el CSV, elimina nulos y duplicados, y arma el grafo completo
def cargar_y_limpiar_datos(ruta_archivo):
    df = pd.read_csv(ruta_archivo, header=None)

    df = df.dropna()
    df = df.drop_duplicates()

    G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])

    return G

# Extrae el subgrafo con los nodos de mayor grado y calcula pesos segun vecinos en comun
def obtener_top_nodos(G, top_n=200):
    grados = dict(G.degree())
    proteinas_mayor_grado = sorted(grados, key=grados.get, reverse=True)[:top_n]

    G_mayor_grado = G.subgraph(proteinas_mayor_grado).copy()
    G_mayor_grado.remove_edges_from(nx.selfloop_edges(G_mayor_grado))

    # La multiplicacion A*A da el numero de vecinos en comun entre cada par de nodos
    A = nx.adjacency_matrix(G_mayor_grado)
    A_cuadrado = A.dot(A)

    nodos_lista = list(G_mayor_grado.nodes())
    nodo_a_indice = {nodo: i for i, nodo in enumerate(nodos_lista)}

    for u, v in G_mayor_grado.edges():
        i = nodo_a_indice[u]
        j = nodo_a_indice[v]

        vecinos_comunes = A_cuadrado[i, j]

        # Convertimos a int nativo para que PyVis pueda serializar el peso a JSON
        peso_calculado = int(500 - vecinos_comunes)
        G_mayor_grado[u][v]['weight'] = peso_calculado

    return G_mayor_grado, None, None