import pandas as pd
import networkx as nx

# Carga el CSV, limpia nulos/duplicados y retorna el grafo completo
def cargar_y_limpiar_datos(ruta_archivo):
    df = pd.read_csv(ruta_archivo, header=None)
    
    # Limpieza de datos
    df = df.dropna() 
    df = df.drop_duplicates() 
    
    # Armar el grafo biologico inicial
    G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])
        
    return G

# Devuelve un subgrafo con los nodos de mayor grado y calcula los pesos matematicamente con matrices.
def obtener_top_nodos(G, top_n=200):
    grados = dict(G.degree())
    proteinas_mayor_grado = sorted(grados, key=grados.get, reverse=True)[:top_n]
    
    G_mayor_grado = G.subgraph(proteinas_mayor_grado).copy()
    G_mayor_grado.remove_edges_from(nx.selfloop_edges(G_mayor_grado))
    
    # --- CALCULO DE PESOS MEDIANTE MATRICES ---
    # 1. Obtenemos la Matriz de Adyacencia del subgrafo
    A = nx.adjacency_matrix(G_mayor_grado)
    
    # 2. Multiplicacion de matrices (A * A) para hallar similitud topologica (vecinos en comun)
    A_cuadrado = A.dot(A)
    
    nodos_lista = list(G_mayor_grado.nodes())
    nodo_a_indice = {nodo: i for i, nodo in enumerate(nodos_lista)}
    
   # 3. Asignamos el peso matematico basado en la matriz resultante
    for u, v in G_mayor_grado.edges():
        i = nodo_a_indice[u]
        j = nodo_a_indice[v]
        
        # Cantidad de proteinas vecinas que u y v comparten
        vecinos_comunes = A_cuadrado[i, j]
        
        # Convertimos a int nativo de Python para que PyVis no colapse al serializar a JSON
        peso_calculado = int(500 - vecinos_comunes)
        G_mayor_grado[u][v]['weight'] = peso_calculado
        
    return G_mayor_grado, None, None