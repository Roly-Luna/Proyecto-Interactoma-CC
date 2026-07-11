import streamlit as st
import networkx as nx
import random
import os
import time
import requests
import tempfile
import streamlit.components.v1 as components
from pyvis.network import Network

# importamos nuestras funciones de los otros archivos
from procesamiento import cargar_y_limpiar_datos, obtener_top_nodos
from dfs import dfs_subgrafo
from kruskal import algoritmo_kruskal

# config de la pagina, layout wide para que se vea mejor el grafo
st.set_page_config(page_title="Interactoma Humano PPI", layout="wide")

# funcion que consulta la api de MyGene para sacar el nombre real de la proteina
# la usamos para que el usuario no vea solo un ID numerico sin sentido
def obtener_info_gen(gene_id):
    try:
        url = f"https://mygene.info/v3/gene/{gene_id}"
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            nombre = datos.get("name", "Nombre biologico no documentado")
            simbolo = datos.get("symbol", "Simbolo desconocido")
            return nombre, simbolo
        return None, None
    except requests.exceptions.RequestException:
        # si falla la conexion o la api no responde, seguimos sin romper la app
        return None, None

# esta funcion arma el grafo interactivo con pyvis para poder mostrarlo en streamlit
def generar_grafo_interactivo(grafo, resaltar_nodo=None):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)
    net.from_nx(grafo)

    for node in net.nodes:
        # el grado nos sirve para mostrar cuantas conexiones tiene la proteina al pasar el mouse
        conexiones = grafo.degree(node['id'])
        node["title"] = f"Proteina ID: {node['id']}\nConexiones en esta red: {conexiones}"
        node["size"] = 15

        # pintamos de rojo y mas grande el nodo que el usuario busco
        if resaltar_nodo and node['id'] == resaltar_nodo:
            node["color"] = "#ff4b4b"
            node["size"] = 25
        else:
            node["color"] = "#1f78b4"

    # quitamos los numeros de peso en las lineas porque se veia muy cargado el grafo
    for edge in net.edges:
        edge['label'] = ""
        edge['value'] = 1
        if 'title' in edge:
            del edge['title']

    # esto evita que los nodos queden todos amontonados en el centro
    net.repulsion(node_distance=150, spring_length=100)

    # pyvis necesita guardar el grafo similar a html para poder mostrarlo, usamos un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        file_path = tmp.name

    net.save_graph(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        html_data = f.read()

    return html_data

# cacheamos la carga del dataset para que no se vuelva a procesar cada vez que se interactua con la app
@st.cache_resource
def iniciar_sistema():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_actual, "..", "Dataset", "PP-Pathways_ppi.csv")
    return cargar_y_limpiar_datos(ruta_csv)

with st.spinner('Construyendo Lista de Adyacencia en Memoria RAM...'):
    G = iniciar_sistema()

st.title("Analisis Computacional del Interactoma Humano")
st.write(f"**Datos procesados:** {G.number_of_nodes()} Proteinas (Nodos) | {G.number_of_edges()} Interacciones (Aristas)")

# logo y panel lateral con las opciones de analisis
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/f/fc/UPC_logo_transparente.png", use_container_width=True)
st.sidebar.header("Opciones de Analisis")

opcion = st.sidebar.selectbox("Seleccione un Algoritmo:",
                              ["Modulo 1: Busqueda de Via (DFS)", "Modulo 2: Esqueleto Vital (Kruskal)"])

# modulo 1, aca hacemos la simulacion de propagacion con DFS
if opcion == "Modulo 1: Busqueda de Via (DFS)":
    st.header("Simulacion de Propagacion en la Red (DFS)")

    col1, col2 = st.columns([1, 3])
    with col1:
        nodo_input = st.number_input("Ingrese ID de Proteina Origen:", min_value=1, value=6334, step=1)
        limite = st.slider("Limite de expansion (Nodos):", 10, 500, 150)
        btn_dfs = st.button("Ejecutar Busqueda de Via")

    with col2:
        if btn_dfs:
            if nodo_input in G:
                with st.spinner('Rastreando propagacion en la red y consultando bases de datos globales...'):

                    # medimos el tiempo real que tarda el DFS para poder reportarlo en el informe
                    tiempo_inicio = time.time()
                    G_dfs = dfs_subgrafo(G, nodo_input, limite_nodos=limite)
                    tiempo_fin = time.time()
                    tiempo_ms = (tiempo_fin - tiempo_inicio) * 1000

                    nombre_prot, simbolo_prot = obtener_info_gen(nodo_input)

                    st.success(f"Via calculada en {tiempo_ms:.2f} milisegundos. Complejidad empirica lograda: O(V + E).")

                    if nombre_prot:
                        st.info(f"Datos Biologicos (En vivo): El gen asociado al ID {nodo_input} es {simbolo_prot} ({nombre_prot}).")

                    st.write(f"**Impacto del fallo:** {G_dfs.number_of_nodes()} nodos afectados mediante {G_dfs.number_of_edges()} interacciones.")

                    html_grafo = generar_grafo_interactivo(G_dfs, resaltar_nodo=nodo_input)
                    components.html(html_grafo, height=620)
            else:
                st.error("Proteina no encontrada en el dataset. Pruebe con otro ID (ej. 6331, 1394).")

# modulo 2, extraemos el arbol de expansion minima con kruskal
elif opcion == "Modulo 2: Esqueleto Vital (Kruskal)":
    st.header("Reduccion del Sistema (MST)")
    st.write("Aplicando el algoritmo de Kruskal apoyado en la estructura Union-Find (UFDS) para identificar las conexiones esenciales sin redundancias.")

    # usamos solo los 200 nodos con mas conexiones, sino el navegador se cuelga al renderizar
    G_mayor_grado, _, _ = obtener_top_nodos(G, 200)

    if st.button("Ejecutar Algoritmo de Kruskal"):
        with st.spinner('Ejecutando Union-Find y extrayendo el arbol minimo...'):

            tiempo_inicio = time.time()
            mst, peso = algoritmo_kruskal(G_mayor_grado)
            tiempo_fin = time.time()
            tiempo_ms = (tiempo_fin - tiempo_inicio) * 1000

            st.success(f"Arbol de Expansion Minima generado en {tiempo_ms:.2f} milisegundos. Complejidad empirica lograda: O(E log E).")
            st.info(f"Metricas de Reduccion: Aristas reducidas de {G_mayor_grado.number_of_edges()} a {mst.number_of_edges()}. Peso estructural total: {peso}")

            html_mst = generar_grafo_interactivo(mst)
            components.html(html_mst, height=620)