

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


# # Filter to include only ARGISSOLO and LATOSSOLO
# #filtered_gdf = gdf_pedo[gdf_pedo['ordem'].isin(['ARGISSOLO', 'LATOSSOLO'])].copy()


# # Start with your specific colors
# color_palette = {
#     'ARGISSOLO': '#1f77b4',
#     'LATOSSOLO': '#ff7f0e',
#     'NEOSSOLO': '#2ca02c',
#     'CAMBISSOLO': '#d62728',
#     'GLEISSOLO': '#9467bd',
#     'PLINTOSSOLO': '#8c564b',
#     'ESPODOSSOLO': '#e377c2',
#     'CHERNOSSOLO': '#7f7f7f',
#     'VERTISSOLO': '#bcbd22',
#     'LUVISSOLO': '#17becf'
# }

# # Get all unique ordem values
# unique_ordens = gdf_pedo['ordem'].unique()

# # Add colors for any missing ordens
# extra_colors = px.colors.qualitative.Alphabet  # Extended color palette
# missing_ordens = [ordem for ordem in unique_ordens if ordem not in color_palette]

# for i, ordem in enumerate(missing_ordens):
#     color_palette[ordem] = extra_colors[i % len(extra_colors)]

# # Create a separate trace for each ordem
# for ordem, color in color_palette.items():
#     if ordem in unique_ordens:  # Only create trace if this ordem exists in data
#         ordem_gdf = gdf_pedo[gdf_pedo['ordem'] == ordem]
        
#         if not ordem_gdf.empty:
#             fig1.add_trace(go.Choroplethmapbox(
#                 geojson=pedology_json,
#                 locations=ordem_gdf.index,
#                 z=[1] * len(ordem_gdf),
#                 colorscale=[(0, color), (1, color)],
#                 showscale=False,
#                 marker_opacity=0.6,
#                 marker_line_width=1,
#                 marker_line_color='black',
#                 hovertemplate=f"<b>Ordem</b>: {ordem}<br><b>Subordem</b>: %{{customdata[0]}}<extra></extra>",
#                 customdata=ordem_gdf[['subordem']],
#                 name=ordem,
#             ))


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

####### --------- ####### ####### --------- ####### 
####### --------- ####### ####### --------- ####### 
 ##### Mapa 2: Produtividade por tipo de pasto #### 
####### --------- ####### ####### --------- ####### 
####### --------- ####### ####### --------- ####### 
import streamlit as st
import geopandas as gpd
import plotly.graph_objects as go
import pandas as pd

st.title("Mapa de Produtividade por Tipo de Pasto (2019–2024)")

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data_media_pasto():
    return gpd.read_file(
        "data/STREAMLIT_media_leite_dia_Vaca_POR_TipoCapim_por_geom.geojson"
    )

gdf = load_data_media_pasto()

# --------------------------------------------------
# Filter capims of interest
# --------------------------------------------------
capins = ['Brachiaria Brizantha', 'Panicum Maximum']

gdf = gdf[gdf['Variedade de Capim utilizada'].isin(capins)].copy()

# Remove invalid values
gdf = (
    gdf
    .dropna(subset=['Produtividade (leite/dia/Vaca)', 'lat', 'lon', 'Ano'])
    .query('`Produtividade (leite/dia/Vaca)` > 0')
)

# --------------------------------------------------
# Helper function to build traces
# --------------------------------------------------
def make_trace(df, capim, color):
    return go.Scattermapbox(
        lat=df['lat'],
        lon=df['lon'],
        mode='markers',
        marker=dict(
            size=df['Produtividade (leite/dia/Vaca)'],
            sizemin=4,
            opacity=0.75
        ),
        name=capim,
        legendgroup=capim,
        hovertemplate=(
            "<b>Capim:</b> " + capim +
            "<br><b>Produtividade:</b> %{marker.size:.2f} L/dia/vaca"
            "<extra></extra>"
        )
    )

# --------------------------------------------------
# Build frames manually (THIS IS THE KEY)
# --------------------------------------------------
years = sorted(gdf['Ano'].unique())
frames = []

for year in years:
    frame_data = []

    for capim in capins:
        df_capim = gdf[
            (gdf['Ano'] == year) &
            (gdf['Variedade de Capim utilizada'] == capim)
        ]

        # Only add trace if data exists for that year
        if not df_capim.empty:
            frame_data.append(
                make_trace(df_capim, capim, None)
            )

    frames.append(
        go.Frame(
            name=str(year),
            data=frame_data
        )
    )

# --------------------------------------------------
# Initial figure (2019)
# --------------------------------------------------
init_year = years[0]
init_traces = []

for capim in capins:
    df_init = gdf[
        (gdf['Ano'] == init_year) &
        (gdf['Variedade de Capim utilizada'] == capim)
    ]
    if not df_init.empty:
        init_traces.append(make_trace(df_init, capim, None))

fig = go.Figure(
    data=init_traces,
    frames=frames
)

# --------------------------------------------------
# Layout
# --------------------------------------------------
fig.update_layout(
    title="Produtividade de Leite por Tipo de Pasto (2019–2024)",
    mapbox=dict(
        style="white-bg",
        zoom=5,
        center=dict(
            lat=gdf['lat'].mean(),
            lon=gdf['lon'].mean()
        ),
        layers=[
            {
                "below": "traces",
                "sourcetype": "raster",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/"
                    "USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ]
    ),
    margin=dict(l=0, r=0, t=60, b=0),
    legend=dict(title="Variedade de Capim"),
    updatemenus=[
        {
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 800, "redraw": True},
                            "transition": {"duration": 300},
                            "fromcurrent": True
                        }
                    ]
                }
            ]
        }
    ],
    sliders=[
        {
            "steps": [
                {
                    "args": [[str(year)], {"frame": {"duration": 0}, "mode": "immediate"}],
                    "label": str(year),
                    "method": "animate"
                }
                for year in years
            ],
            "currentvalue": {"prefix": "Ano: "}
        }
    ]
)

# --------------------------------------------------
# Render
# --------------------------------------------------
st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# st.title("Mapa de Produtividade por Tipo de Pasto")
# lista_tipos_pasto = ['Panicum Maximum', 'Brachiaria Brizantha']
# filtered_gdf_media_tipo_pasto = media_tipo_pasto[media_tipo_pasto['Variedade de Capim utilizada'].isin(lista_tipos_pasto)]
# st.markdown(filtered_gdf_media_tipo_pasto['Variedade de Capim utilizada'].unique())

# # Create second figure

# fig2 = go.Figure()

# for capim in ['Brachiaria Brizantha', 'Panicum Maximum']:
#     df_capim = filtered_gdf_media_tipo_pasto[
#         filtered_gdf_media_tipo_pasto['Variedade de Capim utilizada'] == capim
#     ]

#     fig2.add_trace(
#         go.Scattermapbox(
#             lat=df_capim['lat'],
#             lon=df_capim['lon'],
#             mode='markers',
#             marker=dict(
#                 size=df_capim['Produtividade (leite/dia/Vaca)'],
#                 sizemin=4
#             ),
#             name=capim,
#             hovertext=df_capim['Produtividade (leite/dia/Vaca)'],
#             frame=df_capim['Ano']
#         )
#     )

# # fig2 = px.scatter_mapbox(
# #     filtered_gdf_media_tipo_pasto,
# #     lat="lat",
# #     lon="lon",
# #     color="Variedade de Capim utilizada",
# #     size="Produtividade (leite/dia/Vaca)",
# #     size_max=30,
# #     zoom=5,
# #     # mapbox_style="carto-positron",
# #     width=1200,
# #     height=800,
# #     hover_data={
# #         'Variedade de Capim utilizada': True,
# #         'Produtividade (leite/dia/Vaca)': ':.2f',
# #         'lat': False,
# #         'lon': False
# #     },
    
# #     animation_frame="Ano",
# #     title="Produtividade de Leite por Variedade de Capim ao Longo dos Anos"
# # )

# # # Add pedology layer (as fill)
# # # Create a separate trace for each ordem
# # for ordem, color in color_palette.items():
# #     if ordem in unique_ordens:  # Only create trace if this ordem exists in data
# #         ordem_gdf = gdf_pedo[gdf_pedo['ordem'] == ordem]
        
# #         if not ordem_gdf.empty:
# #             fig2.add_trace(go.Choroplethmapbox(
# #                 geojson=pedology_json,
# #                 locations=ordem_gdf.index,
# #                 z=[1] * len(ordem_gdf),
# #                 colorscale=[(0, color), (1, color)],
# #                 showscale=False,
# #                 marker_opacity=0.6,
# #                 marker_line_width=1,
# #                 marker_line_color='black',
# #                 hovertemplate=f"<b>Ordem</b>: {ordem}<br><b>Subordem</b>: %{{customdata[0]}}<extra></extra>",
# #                 customdata=ordem_gdf[['subordem']],
# #                 name=ordem,
# #             ))

# fig2.update_layout(
#     mapbox_style="white-bg",
#     mapbox_layers=[
#         {
#             "below": 'traces',
#             "sourcetype": "raster",
#             "sourceattribution": "United States Geological Survey",
#             "source": [
#                 "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#             ]
#         }
#       ])

# st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": True})

# # fig_violin2 = px.violin(
# #     media_tipo_pasto,
# #     x="Variedade de Capim utilizada",
# #     y="Produtividade (leite/dia/Vaca)",
# #     box=True,
# #     points="all",
# #     color="Variedade de Capim utilizada",
# #     width=1200,
# #     height=800,
# #     labels={
# #         "Produtividade (leite/dia/Vaca)": "(L/dia/vaca)",
# #         "Variedade de Capim utilizada": "Variedade de Capim"
# #     },
# #     title="Distribuição da Produtividade de Leite por Variedade de Capim"
# # )

# # st.plotly_chart(fig_violin2, use_container_width=True)

# # Estatísticas por tipo de capim
# st.write(
#     filtered_gdf_media_tipo_pasto
#     .groupby('Variedade de Capim utilizada')['Produtividade (leite/dia/Vaca)']
#     .agg(['min', 'mean', 'max'])
# )

# st.write(
#     filtered_gdf_media_tipo_pasto
#     .groupby(['Variedade de Capim utilizada', 'Ano'])['Produtividade (leite/dia/Vaca)']
#     .describe()
# )


# # -------- Estatísticas detalhadas por Tipo de Capim (mantido) --------
# col_prod = "Produtividade (leite/dia/Vaca)"
# col_capim = "Variedade de Capim utilizada"

# valor_maximo = filtered_gdf_media_tipo_pasto[col_prod].max()
# indice_maximo = filtered_gdf_media_tipo_pasto[col_prod].idxmax()
# capim_maximo = filtered_gdf_media_tipo_pasto.loc[indice_maximo, col_capim]

# media_valor = filtered_gdf_media_tipo_pasto[col_prod].mean()
# indice_mais_proximo_media = (filtered_gdf_media_tipo_pasto[col_prod] - media_valor).abs().idxmin()
# capim_mais_proximo_media = filtered_gdf_media_tipo_pasto.loc[indice_mais_proximo_media, col_capim]

# st.subheader("Estatísticas por Tipo de Capim")
# st.markdown(f"""
# - **Valor máximo:** {valor_maximo:.2f} L/dia/vaca (Capim: **{capim_maximo}**)  
# - **Média:** {media_valor:.2f} L/dia/vaca (Capim mais próximo da média: **{capim_mais_proximo_media}**)
# """)

