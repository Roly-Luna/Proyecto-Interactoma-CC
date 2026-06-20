import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random

# ...
from procesamiento import cargar_y_limpiar_datos
from recorridos import bfs_subgrafo

st.title("Visualización del Interactoma")

# 1. Cargar datos
G = cargar_y_limpiar_datos("Dataset/PP-Pathways_ppi.csv")
st.write(f"Total Nodos: {G.number_of_nodes()} | Total Aristas: {G.number_of_edges()}")

# 2. Dibujar la Figura 1
if st.button("Ver Figura 1 (2000 nodos)"):
    random.seed(42)
    nodos_muestra = random.sample(list(G.nodes()), 2000)
    G_muestra = G.subgraph(nodos_muestra).copy()

    plt.figure(figsize=(18, 14))
    pos = nx.spring_layout(G_muestra, seed=42)
    nx.draw(G_muestra, pos, with_labels=False, node_size=5, edge_color="gray", alpha=0.25)
    plt.title("Visualización general de la red con 2000 nodos")
    plt.axis("off")
    
    # En vez de plt.show()
    st.pyplot(plt)