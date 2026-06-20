import pandas as pd
import networkx as nx

def cargar_y_limpiar_datos(ruta_archivo):
    # Cargar el dataset
    df = pd.read_csv(ruta_archivo, header=None)
    # Limpieza de datos
    df = df.dropna()
    df = df.drop_duplicates()
    # Armar el grafo biologico
    G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])
    return G