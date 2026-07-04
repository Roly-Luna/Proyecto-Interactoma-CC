import streamlit as st
import networkx as nx
import random
import os
import time
import requests
import tempfile
import streamlit.components.v1 as components
from pyvis.network import Network

# Importamos nuestros modulos personalizados de las otras clases
from procesamiento import cargar_y_limpiar_datos, obtener_top_nodos
from dfs import dfs_subgrafo
from kruskal import algoritmo_kruskal

# Configuracion inicial de la pagina web
st.set_page_config(page_title="Interactoma Humano PPI", layout="wide")

# --- FUNCIONES NUEVAS PARA EL HITO 3 ---

# 1. Funcion para consumir API publica de genetica (MyGene)
def obtener_info_gen(gene_id):
    # Consulta a internet para obtener el nombre real de la proteina
    try:
        url = f"https://mygene.info/v3/gene/{gene_id}"
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            nombre = datos.get("name", "Nombre biologico no documentado")
            simbolo = datos.get("symbol", "Simbolo desconocido")
            return nombre, simbolo
        return None, None
    except:
        return None, None

# 2. Funcion para generar grafo interactivo con PyVis
def generar_grafo_interactivo(grafo, resaltar_nodo=None):
    # Inicializa red interactiva con fondo blanco y texto negro
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)
    net.from_nx(grafo)
    
    # Configuracion de fisicas y diseno de nodos
    for node in net.nodes:
        # Calculamos el grado del nodo para mostrarlo en el hover
        conexiones = grafo.degree(node['id'])
        
        # Hover interactivo al pasar el mouse con mas informacion
        node["title"] = f"Proteina ID: {node['id']}\nConexiones en esta red: {conexiones}" 
        node["size"] = 15
        
        # Resalta el nodo de origen si existe
        if resaltar_nodo and node['id'] == resaltar_nodo:
            node["color"] = "#ff4b4b" 
            node["size"] = 25
        else:
            node["color"] = "#1f78b4"
            
    # Fuerza de repulsion para evitar que los nodos se amontonen
    net.repulsion(node_distance=150, spring_length=100)
    
    # Crea un archivo temporal seguro en la nube para renderizar el HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        file_path = tmp.name
    
    net.save_graph(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_data = f.read()
        
    return html_data

# --- CARGA EN MEMORIA (CACHE) ---
@st.cache_resource
def iniciar_sistema():
    # Calculamos la ruta absoluta sin importar donde se ejecute
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_actual, "..", "Dataset", "PP-Pathways_ppi.csv")
    return cargar_y_limpiar_datos(ruta_csv)

# Carga de datos masivos
with st.spinner('Construyendo Lista de Adyacencia en Memoria RAM...'):
    G = iniciar_sistema()

# --- DISENO DE INTERFAZ PRINCIPAL ---
st.title("Analisis Computacional del Interactoma Humano")
st.write(f"**Datos procesados:** {G.number_of_nodes()} Proteinas (Nodos) | {G.number_of_edges()} Interacciones (Aristas)")

# --- PANEL LATERAL (SIDEBAR) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/f/fc/UPC_logo_transparente.png", use_container_width=True)
st.sidebar.header("Opciones de Analisis")

# Nombres de menu actualizados
opcion = st.sidebar.selectbox("Seleccione un Algoritmo:", 
                              ["Modulo 1: Busqueda de Via (DFS)", "Modulo 2: Esqueleto Vital (Kruskal)"])

# --- MODULO 1: BUSQUEDA DFS ---
if opcion == "Modulo 1: Busqueda de Via (DFS)":
    st.header("Simulacion de Propagacion en la Red (DFS)")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        nodo_input = st.number_input("Ingrese ID de Proteina Origen:", min_value=1, value=6331, step=1)
        limite = st.slider("Limite de expansion (Nodos):", 10, 500, 150)
        btn_dfs = st.button("Ejecutar Busqueda de Via")
        
    with col2:
        if btn_dfs:
            if nodo_input in G:
                with st.spinner('Rastreando propagacion en la red y consultando bases de datos globales...'):
                    
                    # --- INICIO CRONOMETRO DFS ---
                    tiempo_inicio = time.time()
                    
                    G_dfs = dfs_subgrafo(G, nodo_input, limite_nodos=limite)
                    
                    tiempo_fin = time.time()
                    tiempo_ms = (tiempo_fin - tiempo_inicio) * 1000
                    # --- FIN CRONOMETRO DFS ---
                    
                    # Llamada a la API de biologia
                    nombre_prot, simbolo_prot = obtener_info_gen(nodo_input)
                    
                    st.success(f"Via calculada en {tiempo_ms:.2f} milisegundos. Complejidad empirica lograda: O(V + E).")
                    
                    if nombre_prot:
                        st.info(f"Datos Biologicos (En vivo): El gen asociado al ID {nodo_input} es {simbolo_prot} ({nombre_prot}).")
                    
                    st.write(f"**Impacto del fallo:** {G_dfs.number_of_nodes()} nodos afectados mediante {G_dfs.number_of_edges()} interacciones.")
                    
                    # Renderizado interactivo HTML
                    html_grafo = generar_grafo_interactivo(G_dfs, resaltar_nodo=nodo_input)
                    components.html(html_grafo, height=620)
            else:
                st.error("Proteina no encontrada en el dataset. Pruebe con otro ID (ej. 6331, 1394).")

# --- MODULO 2: KRUSKAL Y UFDS ---
elif opcion == "Modulo 2: Esqueleto Vital (Kruskal)":
    st.header("Reduccion del Sistema (MST)")
    st.write("Aplicando el algoritmo de Kruskal apoyado en la estructura Union-Find (UFDS) para identificar las conexiones esenciales sin redundancias.")
    
    # Extraemos un subgrafo representativo para evitar que el navegador colapse al graficar
    G_mayor_grado, _, _ = obtener_top_nodos(G, 200) 
    
    if st.button("Ejecutar Algoritmo de Kruskal"):
        with st.spinner('Ejecutando Union-Find y extrayendo el arbol minimo...'):
            
            # --- INICIO CRONOMETRO KRUSKAL ---
            tiempo_inicio = time.time()
            
            mst, peso = algoritmo_kruskal(G_mayor_grado)
            
            tiempo_fin = time.time()
            tiempo_ms = (tiempo_fin - tiempo_inicio) * 1000
            # --- FIN CRONOMETRO KRUSKAL ---
            
            st.success(f"Arbol de Expansion Minima generado en {tiempo_ms:.2f} milisegundos. Complejidad empirica lograda: O(E log E).")
            st.info(f"Metricas de Reduccion: Aristas reducidas de {G_mayor_grado.number_of_edges()} a {mst.number_of_edges()}. Peso estructural total: {peso}")
            
            # Renderizado interactivo HTML
            html_mst = generar_grafo_interactivo(mst)
            components.html(html_mst, height=620)