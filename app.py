import streamlit as st
import geopandas as gpd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Mapa de Produtividade de Leite por Vaca")

# Load GeoDataFrame 1
@st.cache_data
def load_data_media_geral():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_por_geom.geojson")

media_geral = load_data_media_geral()

# Plot 1
# Plot 1
fig1 = px.scatter_mapbox(
    media_geral,
    lat="lat",
    lon="lon",
    color="Informação_float",
    size="Informação_float",
    color_continuous_scale=px.colors.sequential.Viridis,
    size_max=15,
    zoom=6,
    mapbox_style="carto-positron",
    width=1200,
    height=800,
    labels={"Informação_float": "(L/dia/vaca)"}
)





st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": True})

# Estatísticas do primeiro mapa
st.subheader("Estatísticas Gerais da Produtividade")
st.markdown(f"""
- **Valor máximo:** {media_geral['Informação_float'].max():.2f} L/dia/vaca  
- **Média:** {media_geral['Informação_float'].mean():.2f} L/dia/vaca
""")


st.title("Mapa de Produtividade por Tipo de Pasto")

# Load GeoDataFrame 2
@st.cache_data
def load_data_por_tipo_pasto():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_POR_TipoCapim_por_geom.geojson")

media_tipo_pasto = load_data_por_tipo_pasto()

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
    title="Produtividade de Leite por Variedade de Capim ao Longo dos Anos"
)


st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": True})

# Estatísticas do segundo mapa
st.subheader("Estatísticas por Tipo de Capim")

# Cálculo dos valores
col_prod = "Produtividade (leite/dia/Vaca)"
col_capim = "Variedade de Capim utilizada"

valor_maximo = media_tipo_pasto[col_prod].max()
indice_maximo = media_tipo_pasto[col_prod].idxmax()
capim_maximo = media_tipo_pasto.loc[indice_maximo, col_capim]

media_valor = media_tipo_pasto[col_prod].mean()
indice_mais_proximo_media = (media_tipo_pasto[col_prod] - media_valor).abs().idxmin()
capim_mais_proximo_media = media_tipo_pasto.loc[indice_mais_proximo_media, col_capim]

st.markdown(f"""
- **Valor máximo:** {valor_maximo:.2f} L/dia/vaca (Capim: **{capim_maximo}**)  
- **Média:** {media_valor:.2f} L/dia/vaca (Capim mais próximo da média: **{capim_mais_proximo_media}**)
""")
