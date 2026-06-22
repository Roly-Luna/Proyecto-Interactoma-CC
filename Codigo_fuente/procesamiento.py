import pandas as pd
import networkx as nx
import random

# Carga el CSV, limpia nulos/duplicados y retorna el grafo completo.
def cargar_y_limpiar_datos(ruta_archivo):
    df = pd.read_csv(ruta_archivo, header=None)
    
    # Limpieza de datos
    df = df.dropna() 
    df = df.drop_duplicates() 
    
    # Armar el grafo biologico
    G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])
    
    # Asignamos pesos aleatorios (1 al 10) para que Kruskal pueda calcular el arbol minimo
    # (Ya que el interactoma original no tiene pesos)
    random.seed(42)
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 10)
        
    return G

# Devuelve un subgrafo con los nodos de mayor grado (Figura 2 de tu Colab).
def obtener_top_nodos(G, top_n=100):
    grados = dict(G.degree())
    proteinas_mayor_grado = sorted(grados, key=grados.get, reverse=True)[:top_n]
    
    G_mayor_grado = G.subgraph(proteinas_mayor_grado).copy()
    G_mayor_grado.remove_edges_from(nx.selfloop_edges(G_mayor_grado))
    
    return G_mayor_grado, proteinas_mayor_grado, grados