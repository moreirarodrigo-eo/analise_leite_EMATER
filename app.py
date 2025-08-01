

import streamlit as st
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")
st.title("Mapa de Produtividade de Leite por Vaca")
st.subheader("Análises realizadas com dados providos pela EMATER - RO")

# Load Data
@st.cache_data
def load_data_media_geral():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_por_geom.geojson")

@st.cache_data
def load_data_media_pasto():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_POR_TipoCapim_por_geom.geojson")

@st.cache_data
def load_pedologia():
    return gpd.read_file("data/pedo_area_uf_ro.geojson")

gdf_geral = load_data_media_geral()
media_tipo_pasto = load_data_media_pasto()
gdf_pedo = load_pedologia()

# Convert to GeoJSON string for Choroplethmapbox
pedology_json = json.loads(gdf_pedo.to_json())


# Mapa 1: Produtividade geral
fig1 = px.scatter_mapbox(
    gdf_geral,
    lat="lat",
    lon="lon",
    color="Informação_float",
    size="Informação_float",
    color_continuous_scale=px.colors.sequential.Viridis,
    range_color=[gdf_geral["Informação_float"].min(), gdf_geral["Informação_float"].max()],
    size_max=15,
    zoom=6,
    # mapbox_style="satellite",
    width=1200,
    height=800,
    labels={"Informação_float": "(L/dia/vaca)", "Ano": "Ano"},
    animation_frame="Ano",
    hover_name="nome" if "nome" in gdf_geral.columns else None,
    title="Produtividade média de leite por localização e ano"
)

# Add pedology layer (as fill)
fig1.add_trace(go.Choroplethmapbox(
    geojson=pedology_json,
    locations=gdf_pedo.index,
    z=[1]*len(gdf_pedo),  # dummy value to show color
    showscale=False,
    marker_opacity=0.3,
    marker_line_width=0.5,
    hovertemplate="<b>Ordem</b>: %{customdata[0]}<br><b>Subordem</b>: %{customdata[1]}<extra></extra>",
    customdata=gdf_pedo[['ordem', 'subordem']],
    name="Pedologia"
))

fig1.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])

st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": True})

# fig_violin = px.violin(
#     gdf_geral,
#     x="Ano",
#     y="Informação_float",
#     box=True,
#     points="all",
#     color="Ano",
#     width=1200,
#     height=800,
#     labels={"Informação_float": "(L/dia/vaca)", "Ano": "Ano"}
# )
# st.plotly_chart(fig_violin, use_container_width=True)

# Estatísticas gerais
st.subheader("Estatísticas Gerais da Produtividade")
st.markdown(f"""
- **Valor máximo:** {gdf_geral['Informação_float'].max():.2f} L/dia/vaca  
- **Média:** {gdf_geral['Informação_float'].mean():.2f} L/dia/vaca
""")

# Mapa 2: Produtividade por tipo de pasto
st.title("Mapa de Produtividade por Tipo de Pasto")

# Create second figure
fig2 = px.scatter_mapbox(
    media_tipo_pasto,
    lat="lat",
    lon="lon",
    color="Variedade de Capim utilizada",
    size="Produtividade (leite/dia/Vaca)",
    size_max=15,
    zoom=5,
    mapbox_style="carto-positron",
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

# Add pedology layer (as fill)
fig2.add_trace(go.Choroplethmapbox(
    geojson=pedology_json,
    locations=gdf_pedo.index,
    z=[1]*len(gdf_pedo),
    showscale=False,
    marker_opacity=0.3,
    marker_line_width=0.5,
    hovertemplate="<b>Ordem</b>: %{customdata[0]}<br><b>Subordem</b>: %{customdata[1]}<extra></extra>",
    customdata=gdf_pedo[['ordem', 'subordem']],
    name="Pedologia"
))

fig1.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])

st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": True})

# fig_violin2 = px.violin(
#     media_tipo_pasto,
#     x="Variedade de Capim utilizada",
#     y="Produtividade (leite/dia/Vaca)",
#     box=True,
#     points="all",
#     color="Variedade de Capim utilizada",
#     width=1200,
#     height=800,
#     labels={
#         "Produtividade (leite/dia/Vaca)": "(L/dia/vaca)",
#         "Variedade de Capim utilizada": "Variedade de Capim"
#     },
#     title="Distribuição da Produtividade de Leite por Variedade de Capim"
# )

# st.plotly_chart(fig_violin2, use_container_width=True)

# Estatísticas por tipo de capim
st.subheader("Estatísticas por Tipo de Capim")

# -------- Estatísticas detalhadas por Tipo de Capim (mantido) --------
col_prod = "Produtividade (leite/dia/Vaca)"
col_capim = "Variedade de Capim utilizada"

valor_maximo = media_tipo_pasto[col_prod].max()
indice_maximo = media_tipo_pasto[col_prod].idxmax()
capim_maximo = media_tipo_pasto.loc[indice_maximo, col_capim]

media_valor = media_tipo_pasto[col_prod].mean()
indice_mais_proximo_media = (media_tipo_pasto[col_prod] - media_valor).abs().idxmin()
capim_mais_proximo_media = media_tipo_pasto.loc[indice_mais_proximo_media, col_capim]

st.subheader("Estatísticas por Tipo de Capim")
st.markdown(f"""
- **Valor máximo:** {valor_maximo:.2f} L/dia/vaca (Capim: **{capim_maximo}**)  
- **Média:** {media_valor:.2f} L/dia/vaca (Capim mais próximo da média: **{capim_mais_proximo_media}**)
""")


