import streamlit as st
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json

st.set_page_config(layout="wide")
st.title("Mapa de Produtividade de Leite por Vaca")
st.subheader("Análises realizadas com dados providos pela EMATER - RO")

# -----------------------------
# Carregar dados
# -----------------------------
@st.cache_data
def load_data_media_geral():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_por_geom.geojson")

@st.cache_data
def load_data_pedologia():
    return gpd.read_file("data/pedo_area_uf_ro.geojson")

@st.cache_data
def load_data_media_pasto():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_POR_TipoCapim_por_geom.geojson")

gdf_geral = load_data_media_geral()
gdf_pedo = load_data_pedologia()
media_tipo_pasto = load_data_media_pasto()

# Certificar que todos estão no mesmo CRS
gdf_pedo = gdf_pedo.to_crs(epsg=4326)
pedology_json = json.loads(gdf_pedo.to_json())

# ------------------------------------------
# MAPA 1: PRODUTIVIDADE + PEDOLOGIA
# ------------------------------------------
fig1 = go.Figure()

# Contorno da pedologia (sem preenchimento)
for feature in pedology_json['features']:
    coords = feature['geometry']['coordinates'][0]
    lon, lat = zip(*coords)
    fig1.add_trace(go.Scattermapbox(
        lon=lon,
        lat=lat,
        mode='lines',
        line=dict(width=1, color='black'),
        hoverinfo='skip',
        showlegend=False
    ))

# Pontos de produtividade
fig1.add_trace(go.Scattermapbox(
    lat=gdf_geral["lat"],
    lon=gdf_geral["lon"],
    mode="markers",
    marker=go.scattermapbox.Marker(
        size=gdf_geral["Informação_float"],
        color=gdf_geral["Informação_float"],
        colorscale="Viridis",
        cmin=gdf_geral["Informação_float"].min(),
        cmax=gdf_geral["Informação_float"].max(),
        showscale=True,
        sizemode="area",
        sizeref=2.*max(gdf_geral["Informação_float"])/(40.**2),
        sizemin=4
    ),
    text=gdf_geral["nome"] if "nome" in gdf_geral.columns else None,
    customdata=gdf_geral[["Informação_float", "Ano"]],
    hovertemplate="<b>Produtividade:</b> %{customdata[0]:.2f} L/dia/vaca<br><b>Ano:</b> %{customdata[1]}<extra></extra>",
    name="Produtividade"
))

fig1.update_layout(
    mapbox=dict(
        style="mapbox://styles/mapbox/satellite-streets-v11",
        zoom=6,
        center=dict(lat=gdf_geral["lat"].mean(), lon=gdf_geral["lon"].mean())
    ),
    margin={"r":0,"t":50,"l":0,"b":0},
    height=800,
    width=1200,
    title="Produtividade média de leite por localização e ano + Pedologia (contorno)"
)

st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": True})

# ------------------------------------------
# VIOLIN PLOT 1
# ------------------------------------------
fig_violin = px.violin(
    gdf_geral,
    x="Ano",
    y="Informação_float",
    box=True,
    points="all",
    color="Ano",
    width=1200,
    height=800,
    labels={"Informação_float": "(L/dia/vaca)", "Ano": "Ano"}
)
st.plotly_chart(fig_violin, use_container_width=True)

st.subheader("Estatísticas Gerais da Produtividade")
st.markdown(f"""
- **Valor máximo:** {gdf_geral['Informação_float'].max():.2f} L/dia/vaca  
- **Média:** {gdf_geral['Informação_float'].mean():.2f} L/dia/vaca
""")

# ------------------------------------------
# MAPA 2: PRODUTIVIDADE POR TIPO DE CAPIM + PEDOLOGIA
# ------------------------------------------
fig2 = px.scatter_mapbox(
    media_tipo_pasto,
    lat="lat",
    lon="lon",
    color="Variedade de Capim utilizada",
    size="Produtividade (leite/dia/Vaca)",
    size_max=15,
    zoom=5,
    mapbox_style="mapbox://styles/mapbox/satellite-streets-v11",
    width=1200,
    height=800,
    hover_data={
        'Variedade de Capim utilizada': True,
        'Produtividade (leite/dia/Vaca)': ':.2f',
        'lat': False,
        'lon': False
    },
    animation_frame="Ano",
    title="Produtividade de Leite por Variedade de Capim ao Longo dos Anos"
)

# Adiciona contornos da pedologia ao fig2 manualmente
for feature in pedology_json['features']:
    coords = feature['geometry']['coordinates'][0]
    lon, lat = zip(*coords)
    fig2.add_trace(go.Scattermapbox(
        lon=lon,
        lat=lat,
        mode='lines',
        line=dict(width=1, color='black'),
        hoverinfo='skip',
        showlegend=False
    ))

st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": True})

# ------------------------------------------
# VIOLIN PLOT 2
# ------------------------------------------
fig_violin2 = px.violin(
    media_tipo_pasto,
    x="Variedade de Capim utilizada",
    y="Produtividade (leite/dia/Vaca)",
    box=True,
    points="all",
    color="Variedade de Capim utilizada",
    width=1200,
    height=800,
    labels={
        "Produtividade (leite/dia/Vaca)": "(L/dia/vaca)",
        "Variedade de Capim utilizada": "Variedade de Capim"
    },
    title="Distribuição da Produtividade de Leite por Variedade de Capim"
)
st.plotly_chart(fig_violin2, use_container_width=True)

# ------------------------------------------
# ESTATÍSTICAS POR CAPIM
# ------------------------------------------
st.subheader("Estatísticas por Tipo de Capim")
col_prod = "Produtividade (leite/dia/Vaca)"
c
