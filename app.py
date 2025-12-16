import streamlit as st
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")
st.title("Mapa de Produtividade de Leite por Vaca")
st.subheader("Análises realizadas com dados providos pela EMATER - RO")

# Load GeoDataFrames
@st.cache_data
def load_data_media_geral():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_por_geom.geojson")

@st.cache_data
def load_data_pedologia():
    return gpd.read_file("data/pedo_area_uf_ro.geojson", engine="fiona")

gdf_geral = load_data_media_geral()
gdf_pedo = load_data_pedologia()

# Ensure pedology layer is in lat/lon
gdf_pedo = gdf_pedo.to_crs(epsg=4326)
pedology_json = json.loads(gdf_pedo.to_json())

# ---- FIGURE 1 WITH PEDOLOGY LAYER ----
fig1 = go.Figure()

# Add pedology background layer
fig1.add_trace(go.Choroplethmapbox(
    geojson=pedology_json,
    locations=gdf_pedo.index,
    z=[1] * len(gdf_pedo),  # Dummy values for display
    showscale=False,
    marker_opacity=0.3,
    marker_line_width=0.5,
    customdata=gdf_pedo[["ordem", "subordem"]],
    hovertemplate="<b>Ordem:</b> %{customdata[0]}<br><b>Subordem:</b> %{customdata[1]}<extra></extra>",
    name="Pedologia"
))

# Add scatter points for productivity
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
        style="carto-positron",
        zoom=6,
        center=dict(lat=gdf_geral["lat"].mean(), lon=gdf_geral["lon"].mean())
    ),
    margin={"r":0,"t":50,"l":0,"b":0},
    height=800,
    width=1200,
    title="Produtividade média de leite por localização e ano + Pedologia"
)

st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": True})

# ---- VIOLIN PLOT ----
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

# ---- ESTATÍSTICAS ----
st.subheader("Estatísticas Gerais da Produtividade")
st.markdown(f"""
- **Valor máximo:** {gdf_geral['Informação_float'].max():.2f} L/dia/vaca  
- **Média:** {gdf_geral['Informação_float'].mean():.2f} L/dia/vaca
""")

# -----------------------------------------
# --------- SEGUNDO MAPA: PASTO ----------
# -----------------------------------------
st.title("Mapa de Produtividade por Tipo de Pasto")

@st.cache_data
def load_data_media_pasto():
    return gpd.read_file("data/STREAMLIT_media_leite_dia_Vaca_POR_TipoCapim_por_geom.geojson")

media_tipo_pasto = load_data_media_pasto()

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

st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": True})

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

# ---- ESTATÍSTICAS TIPO CAPIM ----
st.subheader("Estatísticas por Tipo de Capim")
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
