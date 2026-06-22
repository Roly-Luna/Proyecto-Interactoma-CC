import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random

# Importamos nuestros modulos personalizados
from procesamiento import cargar_y_limpiar_datos, obtener_top_nodos
from dfs import dfs_subgrafo
from kruskal import algoritmo_kruskal

st.set_page_config(page_title="Interactoma Humano PPI", layout="wide")

# --- CARGA EN MEMORIA (CACHE) ---
@st.cache_resource
def iniciar_sistema():
    # leer el CSV
    return cargar_y_limpiar_datos("../Dataset/PP-Pathways_ppi.csv")

with st.spinner('Construyendo Lista de Adyacencia en Memoria RAM...'):
    G = iniciar_sistema()

# --- DISENO DE INTERFAZ ---
st.title("🧬 Analisis Computacional del Interactoma Humano")
st.write(f"**Datos procesados:** {G.number_of_nodes()} Proteinas (Nodos) | {G.number_of_edges()} Interacciones (Aristas)")

# Sidebar Menu
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Protein-protein_interaction_network.png/300px-Protein-protein_interaction_network.png", use_container_width=True)
st.sidebar.title("Modulos Algoritmicos")
opcion = st.sidebar.radio("Seleccione el analisis:", 
                          ["1. Exploracion Inicial (Grafo General)", 
                           "2. Deteccion de Hubs", 
                           "3. Simulacion de Via (DFS)", 
                           "4. Esqueleto Vital (Kruskal - MST)"])

# --- LOGICA DE VISUALIZACION ---

if opcion == "1. Exploracion Inicial (Grafo General)":
    st.header("Figura 1: Muestra Representativa (2000 nodos)")
    if st.button("Renderizar Grafo"):
        random.seed(42)
        nodos_muestra = random.sample(list(G.nodes()), 2000)
        G_muestra = G.subgraph(nodos_muestra).copy()
        
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.spring_layout(G_muestra, seed=42)
        nx.draw(G_muestra, pos, with_labels=False, node_size=5, edge_color="gray", alpha=0.25, ax=ax)
        ax.set_title("Interactoma - Muestra Aleatoria")
        st.pyplot(fig)

elif opcion == "2. Deteccion de Hubs":
    st.header("Figura 2: Proteinas Criticas (Mayor Grado)")
    G_mayor_grado, proteinas_top, grados = obtener_top_nodos(G, 100)
    
    st.info(f"Proteina mas conectada: **ID {proteinas_top[0]}** con {grados[proteinas_top[0]]} interacciones.")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G_mayor_grado, seed=42, k=0.8, iterations=80)
    nx.draw_networkx_edges(G_mayor_grado, pos, edge_color="gray", alpha=0.35, width=0.8, ax=ax)
    nx.draw_networkx_nodes(G_mayor_grado, pos, node_size=70, alpha=0.85, node_color="orange", ax=ax)
    st.pyplot(fig)

elif opcion == "3. Simulacion de Via (DFS)":
    st.header("Figura 3: Rastreo de Via de Senalizacion con DFS")
    nodo_input = st.number_input("Ingresa el ID de la Proteina de origen:", value=6331, step=1)
    
    if st.button("Ejecutar Busqueda en Profundidad (DFS)"):
        if nodo_input in G.nodes():
            G_dfs = dfs_subgrafo(G, nodo_inicial=nodo_input, limite_nodos=150)
            st.success(f"Recorrido exitoso. Nodos impactados: {G_dfs.number_of_nodes()}")
            
            fig, ax = plt.subplots(figsize=(14, 10))
            pos = nx.spring_layout(G_dfs, seed=42)
            nx.draw(G_dfs, pos, with_labels=False, node_size=50, edge_color="red", alpha=0.45, ax=ax)
            # Nodo de origen mas grande
            nx.draw_networkx_nodes(G_dfs, pos, nodelist=[nodo_input], node_size=200, node_color="black", ax=ax)
            st.pyplot(fig)
        else:
            st.error("Proteina no encontrada en el dataset.")

elif opcion == "4. Esqueleto Vital (Kruskal - MST)":
    st.header("Figura 4: Reduccion del Sistema (MST)")
    st.write("Aplicando Kruskal y UFDS para identificar las conexiones esenciales sin ciclos redundantes.")
    
    # Aplicamos Kruskal a los Hubs para que la web no se congele dibujando 300k aristas
    G_mayor_grado, _, _ = obtener_top_nodos(G, 200) 
    
    if st.button("Ejecutar Algoritmo de Kruskal"):
        mst, peso = algoritmo_kruskal(G_mayor_grado)
        st.success(f"MST generado. Aristas reducidas de {G_mayor_grado.number_of_edges()} a {mst.number_of_edges()}. Peso estructural: {peso}")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        pos = nx.spring_layout(mst, seed=42)
        nx.draw_networkx_edges(mst, pos, edge_color="green", width=1.5, ax=ax)
        nx.draw_networkx_nodes(mst, pos, node_size=60, node_color="lightblue", ax=ax)
        st.pyplot(fig)