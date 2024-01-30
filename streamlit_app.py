import numpy as np
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import geopandas as gpd
from shapely.wkt import loads
import plotly.express as px
import shapely
import asyncio
from contextlib import contextmanager



st.set_page_config(page_title="", page_icon="🗺️")
st.sidebar.title("UrbanFlow Milano 🔀")

locations = pd.read_csv('./newdata.csv')
locations = locations[locations['Partenza'] != locations['Arrivo']]
locations = locations[locations['Arrivo'] !='ROSERIO']

locations = locations.sort_values(by=['Arrivo', 'conteggio'], ascending=[True, False])
locations = locations.groupby('Arrivo').head(3)

nil = pd.read_csv('./nil_milano.csv')

risultato = locations.groupby('Arrivo')['conteggio'].sum()
nil.dropna()
nil['viaggi'] = nil['NIL'].map(risultato)
nil['viaggi'] = (nil['viaggi'].fillna(0))
nil = nil[nil['viaggi']> 0]
totale_viaggi = sum(nil['viaggi'])
nil['colori'] = ["#580000", "#5d0500", "#681101", "#711b03", "#7b2406", "#832d09", "#8c350b", "#943d0f", "#9b4411", "#a34b14", "#ab5217", "#b25a19", "#b9601c", "#bf681e", "#c66f21", "#cc7522", "#d37b25", "#d98127", "#dd892f", "#e0913d", "#e2984a", "#e4a055", "#e6a760", "#e7ae6a", "#e9b573", "#ebbc7d", "#edc287", "#eec890", "#efcd99", "#f1d3a1", "#f2d8a7", "#f3ddae", "#f5e1b6", "#f6e5bc", "#f7eac1", "#f8edc7", "#f9f1cc", "#faf4d0", "#fbf6d3", "#fcf8d8", "#fdfbdb", "#fdfcdc", "#fdfddd", "#fefede", "#ffffe0", "#fdfedf", "#fcfdde", "#fbfcde", "#f9fbdd", "#f6fadd", "#f3f9dc", "#f0f6db", "#edf4da", "#e9f2d9", "#e3efd7", "#dfecd6", "#dae9d4", "#d4e6d2", "#cfe3d0", "#c9dfce", "#c1dbca", "#bbd7c8", "#b4d3c5", "#accfc2", "#a3cbbe", "#9cc7bc", "#92c2b8", "#88beb5", "#7dbab2", "#72b5af", "#63b1ab", "#53aca8", "#42a8a6", "#3ba1a0", "#389a99", "#359392", "#328c8b", "#2f8585", "#2c7e7e", "#287777"]

def popup_html(row):
    nil_name = nil['NIL'][row]
    tot_viaggi = []
    provenienze = []

    for index, row in (locations[locations['Arrivo'] == nil_name]).iterrows():
        provenienze.append(row['Partenza'])
        tot_viaggi.append(row['conteggio'])



    html = """<!DOCTYPE html>
<html>
<head>
<h4 style="margin-bottom:10">{}</h4>""".format(nil_name) + """
</head>
    <table>
<thead style="border: 1px solid #E1E4E9;">
    <tr style="background-color:#F7F9FD; color:#464F60">
      <th style="border-right:1px solid #E1E4E9; padding:8px">Ranking</th>
      <th style="padding:8px;border-right:1px solid #E1E4E9;">Origine</th>
      <th style="padding:8px">N. viaggi</th>
    </tr>
  </thead>
<tr style="background-color:white; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#1</td>
<td style="padding:8px">{}</td>""".format(provenienze[0])+"""
<td style="padding:8px">{}</td>""".format(tot_viaggi[0])+"""
</tr>
<tr style="background-color:#F9FAFC; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#2</td>
<td style="padding:8px">{}</td>""".format(provenienze[1])+"""
<td style="padding:8px">{}</td>""".format(tot_viaggi[1])+"""
</tr>
<tr style="background-color:white; border-width: 0 1px 1px 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#3</td>
<td style="padding:8px">{}</td>""".format(provenienze[2])+"""
<td style="padding:8px">{}</td>""".format(tot_viaggi[2])+"""
</tr>

</table>
</html>
"""
    return html




def print_map():
    st.title('OD Flow Map')

    st.info("""I punti visualizzati sulla mappa indicano i Nuclei di Identità Locale (NIL) del comune di Milano; le linee rappresentano invece i viaggi effettuati nel luglio 2023 tramite car-sharing, biciclette, scooter e monopattini condivisi.
    """, icon="ℹ️")
    m = folium.Map(zoom_start=14, location=(45.467250, 9.189686))
    #codice delle linee preso da https://statesmigrate.streamlit.app/
    for index, row in locations.iterrows():
        selected_row = nil[nil['NIL'] == row['Partenza']]
        opaq = 100*(row['conteggio'] / int(totale_viaggi))
        opaq = max(0.05, opaq)
        colore = selected_row['colori'].to_list()



        poly = folium.PolyLine(locations=[[row['x_partenza'], row['y_partenza']],
                                          [row['x_arrivo'], row['y_arrivo']]], opacity=opaq, color=colore)

        poly.add_to(m)
        l = 0.0014  # the arrow length
        widh = 0.000042  # 2*widh is the width of the arrow base as triangle

        A = np.array([row['x_partenza'], row['y_partenza']])
        B = np.array([row['x_arrivo'], row['y_arrivo']])

        v = B - A

        w = v / np.linalg.norm(v)
        u = np.array([-w[1], w[0]]) * 10  # u orthogonal on  w

        P = B - l * w
        S = P - widh * u
        T = P + widh * u

        pointA = (S[0], S[1])
        pointB = (T[0], T[1])
        pointC = (B[0], B[1])

        points = [pointA, pointB, pointC, pointA]

        folium.PolyLine(locations=points, opacity=opaq, fill=True, color=colore).add_to(m)


    for index1, row1 in nil.iterrows():
        html = popup_html(index1)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Circle(location=[row1['quartieri_centroidi_X'], row1['quartieri_centroidi_Y']], color='black',weight=0.6, fill_opacity=1, fill_color=[row1['colori']], radius=50, popup=popup).add_to(m)


    folium.plugins.ScrollZoomToggler().add_to(m)
    m.save("prova.html")
    HtmlFile = open("prova.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, width=704, height=600, scrolling=True)





def visualizza_mappa():
    st.title('Trajectory Flow Map')
    df_milano = gpd.read_file('./viaggi_milano_sample.csv')

    with st.form("my_form"):
        option = st.selectbox('Seleziona un quartiere',(df_milano['Arrivo'].unique()), index=40)
        direzione = st.radio("Direzione dei flussi",["Entrata", "Uscita"], index=0)

        submitted = st.form_submit_button("Genera mappa")

    if submitted:
        if direzione == 'Entrata':
            flow = 'Arrivo'
        else:
            flow = 'Partenza'

        df_milano = df_milano[df_milano[flow] == option]



        df_milano['geom_wkt_estimated_route'] = df_milano['geom_wkt_estimated_route'].apply(loads)

        df_milano = gpd.GeoDataFrame(df_milano, geometry='geom_wkt_estimated_route', crs='EPSG:4326')
        exploded =df_milano.explode('geom_wkt_estimated_route')

        lats = []
        lons = []
        names = []
        vehicles = []
        for feature, name,vehicle in zip(exploded.geometry, exploded.id, exploded.type_vehicle):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name]*len(y))
                vehicles = np.append(vehicles, [vehicle]*len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
                vehicles = np.append(vehicles, None)

        newnames = {'C':'Auto (C)', 'B': 'Bici (B)', 'M':'Scooter (M)', 'S':'Monopattini (S)'}
        fig = px.line_mapbox(lat=lats, lon=lons, width=704, height=600,
                             mapbox_style="dark",  line_group=names, color=vehicles, labels={'line_group': 'ID', 'color':'Mezzo', },)

        fig.update_layout(mapbox_zoom=10, legend_itemclick='toggleothers', legend_title_text='Mezzi di trasporto')
        fig.update_mapboxes(accesstoken="pk.eyJ1IjoiZGVsZm8xIiwiYSI6ImNsbmx1YzB6MzJwNDgya3JsZzJsZjc1YWwifQ.6nVOkmTdDbEXbOPu3twfwA")
        fig.update_traces(opacity=0.6)

        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        st.plotly_chart(fig)



def chord_diagram():
    st.title('Chord Diagram')

    # Codice per risolvere errore compatibilità Streamlit
    @contextmanager
    def setup_event_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            yield loop
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    
    with setup_event_loop() as loop:
        import holoviews as hv


    options = st.multiselect(
    'Quali veicoli vuoi visualizzare?',
        ['Bici', 'Auto', 'Monopattini', 'Scooter'],
        ['Bici','Auto', 'Monopattini', 'Scooter']
    )

    dictionary_opts = {
        'Bici': 'B',
        'Auto': 'C',
        'Monopattini':'M',
        'Scooter': 'S'
    }


    lista_input = []

    for i in options:
        lista_input.append(dictionary_opts[i])

    viaggi_min = st.slider('Numero minimo di viaggi tra due quartieri', 20, 75, 30, step= 15)


    hv.extension('bokeh')

    census_data = pd.read_csv('./nuovo_dataframe2.csv')
    census_data = census_data[census_data['Partenza'] != census_data['Arrivo']]

    filtered_df = census_data[census_data['Viaggi'] >= viaggi_min]

    filtered_df = filtered_df[filtered_df['type_vehicle'].isin(lista_input)]

    filtered_df = filtered_df.drop(columns='type_vehicle')

    filtered_df = filtered_df.groupby(['Partenza','Arrivo'])['Viaggi'].sum().reset_index()
    colonna_unique = set(filtered_df['Partenza'])
    colonna_unique.update(filtered_df['Arrivo'])
    colonna_unique= list(colonna_unique)



    st.write(filtered_df, use_container_width=True)



    n = 0
    dizionario = {}
    for i in colonna_unique:
        dizionario[i] = n
        n+=1



    links = filtered_df.replace({'Partenza':dizionario,
                                'Arrivo': dizionario})




    nodes = pd.DataFrame({'index': dizionario.values(), 'name': dizionario.keys()})

    #filtered_df.rename(columns={"Viaggi": "values"})


    nodes = hv.Dataset(nodes, 'index')

    chord = hv.Chord((links, nodes))

    chord.opts(cmap='Category20', edge_cmap='Category20', edge_color="Partenza", labels="name", node_color="index", width=600, height=600)

    hv.save(chord ,'fig.html')
    HtmlFile = open("fig.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, width=704, height=704, scrolling=True)





page_name_functions = {
            "OD Flow Map": print_map,
            "Trajectory Flow Map": visualizza_mappa,
            "Chord Diagram": chord_diagram,
        }
selected_page = st.sidebar.selectbox("Seleziona una pagina", page_name_functions.keys())

st.sidebar.write("""
                 ## About
                 UrbanFlow Milano permette di esplorare i flussi di mobilità sostenibile attraverso la visualizzazione dei viaggi effettuati con servizi di car-sharing, biciclette, scooter e monopattini condivisi.""")
page_name_functions[selected_page]()