import numpy as np
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from shapely.wkt import loads
import shapely
import asyncio
from contextlib import contextmanager
import datetime

from bokeh.themes.theme import Theme
from bokeh.models import HoverTool


st.set_page_config(page_title="UrbanFlow Milano", page_icon="🔀️", layout='wide', initial_sidebar_state='expanded')
st.sidebar.title("🔀 UrbanFlow Milano")


def introduzione():
    st.title('🔀 UrbanFlow Milano ')
    with st.container():
        st.write(
            "UrbanFlow Milano è un'applicazione web interattiva realizzata con Streamlit nell'ambito di un progetto di tesi. L'obiettivo è quello di sperimentare e presentare diverse modalità di visualizzazione di dati inerenti alla mobilità sostenibile. L'applicazione è pensata per essere fruita da desktop e si articola in quattro pagine: Introduzione, OD Flow Map, Trajectory Flow Map e Chord Diagram.")

        st.write(
            "I dati visualizzati sono forniti da Fluctuo e riguardano gli spostamenti avvenuti con mezzi condivisi nel comune di Milano durante il mese di luglio 2023. Alle coordinate geografiche di partenza e di destinazione sono stati assegnati i rispettivi NIL, in modo da poter avere un'aggregazione dei viaggi. Per ottimizzare le prestazioni, l'app mostra soltanto un campione dei dati completi. Le informazioni visualizzate non sono pertanto sufficienti per trarre conclusioni definitive sulla mobilità di Milano. L'app può tuttavia offrire uno spunto di riflessione per tecnologie e forme di interazioni utili a progetti futuri.")
        with st.expander("**Cosa sono i NIL?**"):
            st.write(
                "I NIL, o Nuclei di Identità Locale, sono una suddivisione territoriale del Comune di Milano introdotta con il Piano di Governo del Territorio (PGT) 2030. Sono in totale 88 e rappresentano le unità minime di programmazione previste dal piano.")

        st.header('Overview')

        st.markdown('''
    
            - [OD Flow Map](#od-flow-map)
            - [Trajectory Flow Map](#trajectory-flow-map)
            - [Chord Diagram](#chord-diagram)
            ''', unsafe_allow_html=True)

        st.subheader('OD Flow map')
        st.image('img/tutorial1.png',
                 caption='Sidebar per la scelta dei filtri (A); popup (B) con il ranking delle 3 maggiori connessioni in entrata e uscita.',
                 use_column_width='auto')
        st.write(
            "L'OD flow map è uno strumento utile per visualizzare le interconnessioni tra i diversi NIL. Di seguito vengono elencati i principali elementi presenti nella sidebar e nel pannello di visualizzazione. ")
        st.markdown('''



#### Sidebar:
- **Filtra collegamenti in:** permette di scegliere se filtrare i collegamenti in entrata oppure quelli in uscita.
- **Numero massimo di collegamenti in Entrata/Uscita:** limita il numero di collegamenti che partono o arrivano ad ogni singolo nodo. Per evitare il sovraffollamento visivo, il valore è impostato di default a 3.
- **Opacità minima dei collegamenti:** consente di personalizzare l'opacità minima dei collegamenti, il suo valore predefinito è 0.05.

#### Pannello di visualizzazione:
- **Frecce**: ogni freccia simboleggia un collegamento tra due NIL, con il colore determinato dal nodo di origine e l'intensità legata all'ammontare del flusso.
- **Punti**: ogni NIL è rappresentato da un punto colorato, la cui posizione è stata ricavata calcolandone il centroide.
- **Popup**: cliccando su un nodo, è possibile visualizzare un popup che mostra le prime tre connessioni in entrata e in uscita, in base al tab selezionato.
                ''', unsafe_allow_html=True)

        st.write("---")
        st.subheader('Trajectory Flow map')
        st.image('img/tutorial2.png',
                 caption='Sidebar per filtrare i dati e generare la mappa (A); legenda con filtro della tipologia dei viaggi (B).',
                 use_column_width='auto')
        st.write(
            "La Trajectory Map è uno strumento utile per visualizzare i tracciati dei viaggi che hanno come origine o destinazione il NIL selezionato. Di seguito vengono elencati i principali elementi presenti nella sidebar e nel pannello di visualizzazione.")
        st.markdown("""
#### Sidebar:
- **Seleziona un NIL**: permette di scegliere il NIL di cui si desidera visualizzare i viaggi.
- **Direzione dei flussi**: permette di scegliere se visualizzare i viaggi in entrata o in uscita dal NIL selezionato.
- **Intervallo di tempo**: consente di personalizzare l'intervallo temporale dei dati visualizzati. È possibile specificare le date e gli orari di inizio e di fine. 
- **Stile mappa**: permette di personalizzare l'aspetto della mappa in base alle preferenze dell'utente. Le opzioni disponibili includono dark, light, satellite e open-street-map.
#### Pannello di visualizzazione:

- **Linee**: le linee rappresentano i percorsi dei viaggi, il colore indica la tipologia di mezzo utilizzato, mentre l'opacità ne riflette l'ammontare.
- **Legenda**: la legenda mostra la corrispondenza tra colori e mezzi di trasporto. Cliccando su una delle voci, è possibile filtrare la visualizzazione.
                    """)
        st.write("---")
        st.subheader('Chord Diagram')
        st.image('img/tutorial3.png',
                 caption="Sidebar per l'impostazione dei filtri (A); tab per la scelta della visualizzazione (B).",
                 use_column_width='auto')
        st.write(
            "Il Chord Diagram è un grafico circolare che evidenzia le relazioni tra entità mediante archi di grandezza variabile. In questa specifica visualizzazione, i nodi (punti sul bordo) rappresentano i NIL, mentre gli archi indicano il numero di viaggi effettuati.")
        st.markdown("""
        #### Sidebar:
        - **Quali veicoli vuoi visualizzare?**: questa opzione permette di selezionare la tipologia di veicoli da visualizzare nel grafico.
        - **Numero minimo di viaggi tra due quartieri**: questa opzione permette di visualizzare soltanto quei collegamenti che hanno un numero di collegamenti pari o superiore al numero selezionato.
        #### Pannello di visualizzazione:
        - **Tab**: questa opzione permette di alternare la visualizzazione del grafico a quella della tabella corrispondente, così da ottenere dettagli più precisi circa l'ammontare dei viaggi tra i NIL.
        - **Archi**: gli archi rappresentano i collegamenti tra i NIL. Il loro colore indica il nodo di origine mentre l'ampiezza evidenzia l'entità dello scambio. 
        - **Punti**: ogni punto rappresenta un NIL ed è reso riconoscibile da un colore specifico.
        """)
        placeholder.empty()


def print_map():
    with st.sidebar:
        direzione_viaggio = st.radio(
            "Filtra collegamenti in:",
            ["Entrata", "Uscita"])

        if direzione_viaggio == 'Uscita':
            direzione_viaggio_m = 'Partenza'
        else:
            direzione_viaggio_m = 'Arrivo'


        max_col = st.slider('Numero massimo di collegamenti in ' + direzione_viaggio, 0, 73, 3,
                        help="Il limite è applicato a tutti i NIL presenti sulla mappa.")
        opaq_minima = st.slider("Opacità minima dei collegamenti", 0.0,
                                1.0,
                                0.05, help="Incrementa l'opacità per rendere visibili i collegamenti con pochi viaggi.")

    st.title('OD Flow Map')

    locations = pd.read_csv('newdata.csv')
    locations = locations[locations['Partenza'] != locations['Arrivo']]

    partenze_popup = locations.sort_values(by=['Partenza', 'conteggio'], ascending=[True, False])

    arrivi_popup = locations.sort_values(by=['Arrivo', 'conteggio'], ascending=[True, False])

    partenze_popup = partenze_popup.groupby('Partenza').head(3)

    arrivi_popup = arrivi_popup.groupby('Arrivo').head(3)

    locations = locations.sort_values(by=[direzione_viaggio_m, 'conteggio'], ascending=[True, False])

    locations = locations.groupby(direzione_viaggio_m).head(max_col)

    nil_milano = pd.read_csv('nil_milano.csv')

    risultato = locations.groupby(direzione_viaggio_m)['conteggio'].sum()

    nil_milano.dropna()
    nil_milano['viaggi'] = nil_milano['NIL'].map(risultato)

    nil_milano['viaggi'] = (nil_milano['viaggi'].fillna(0))
    nil_milano = nil_milano[nil_milano['viaggi'] > 0]
    totale_viaggi = sum(nil_milano['viaggi'])
    nil_milano['colori'] = ["#580000", "#5d0500", "#681101", "#711b03", "#7b2406", "#832d09", "#8c350b", "#943d0f",
                         "#9b4411", "#a34b14", "#ab5217", "#b25a19", "#b9601c", "#bf681e", "#c66f21", "#cc7522",
                         "#d37b25", "#d98127", "#dd892f", "#e0913d", "#e2984a", "#e4a055", "#e6a760", "#e7ae6a",
                         "#e9b573", "#ebbc7d", "#edc287", "#eec890", "#efcd99", "#f1d3a1", "#f2d8a7", "#f3ddae",
                         "#f5e1b6", "#f6e5bc", "#f7eac1", "#f8edc7", "#f9f1cc", "#faf4d0", "#fbf6d3", "#fcf8d8",
                         "#fdfbdb", "#fdfcdc", "#fdfddd", "#fefede", "#ffffe0", "#fdfedf", "#fcfdde", "#fbfcde",
                         "#f9fbdd", "#f6fadd", "#f3f9dc", "#f0f6db", "#edf4da", "#e9f2d9", "#e3efd7", "#dfecd6",
                         "#dae9d4", "#d4e6d2", "#cfe3d0", "#c9dfce", "#c1dbca", "#bbd7c8", "#b4d3c5", "#accfc2",
                         "#a3cbbe", "#9cc7bc", "#92c2b8", "#88beb5", "#7dbab2", "#72b5af", "#63b1ab", "#53aca8",
                         "#42a8a6", "#3ba1a0", "#389a99", "#359392", "#328c8b", "#2f8585", "#2c7e7e", "#287777",
                         '#b53a37', '#16e517'][0:len(nil_milano)]

    def popup_html(row):
        institution_name = nil_milano['NIL'][row]

        tot_origini = []
        tot_destinazioni = []
        origini = []
        destinazioni = []

        for index, row in (partenze_popup[partenze_popup['Partenza'] == institution_name]).iterrows():
            origini.append(row['Arrivo'])
            tot_origini.append(row['conteggio'])

        for index, row in (arrivi_popup[arrivi_popup['Arrivo'] == institution_name]).iterrows():
            destinazioni.append(row['Partenza'])
            tot_destinazioni.append(row['conteggio'])

        len_check_origini = len(origini)
        len_check_destinazioni = len(destinazioni)


        html = """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    
<h4 style="margin-bottom:10">{}</h4>""".format(institution_name) + """
  <ul  class="nav nav-tabs" >
    <li class="nav-link active" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">Origini</li>
    <li class="nav-link" id="nav-profile-tab" data-bs-toggle="tab" data-bs-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">Destinazioni</li>
  </ul>
<div class="tab-content" id="nav-tabContent">
  <div style="opacity:1" class="tab-pane show active" id="nav-home" role="tabpanel" aria-labelledby="nav-home-tab">
    <table >
<thead style="border: 1px solid #E1E4E9;">
    <tr style="background-color:#F7F9FD; color:#464F60">
      <th style="border-right:1px solid #E1E4E9; padding:8px">Ranking</th>
      <th style="padding:8px;border-right:1px solid #E1E4E9;">Origini</th>
      <th style="padding:8px">N. viaggi</th>
    </tr>
  </thead>
<tr style="background-color:white; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#1</td>
<td style="padding:8px">{}</td>""".format(destinazioni[0] if len_check_destinazioni > 0 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinazioni[0] if len_check_destinazioni > 0 else '//') + """
</tr>
<tr style="background-color:#F9FAFC; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#2</td>
<td style="padding:8px">{}</td>""".format(destinazioni[1] if len_check_destinazioni > 1 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinazioni[1] if len_check_destinazioni > 1 else '//') + """
</tr>
<tr style="background-color:white; border-width: 0 1px 1px 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#3</td>
<td style="padding:8px">{}</td>""".format(destinazioni[2] if len_check_destinazioni > 2 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinazioni[2] if len_check_destinazioni > 2 else '//') + """
</tr>
</table>
  </div>
  <div style="opacity:1" class="tab-pane " id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <table>
<thead style="border: 1px solid #E1E4E9;">
    <tr style="background-color:#F7F9FD; color:#464F60">
      <th style="border-right:1px solid #E1E4E9; padding:8px">Ranking</th>
      <th style="padding:8px;border-right:1px solid #E1E4E9;">Destinazioni</th>
      <th style="padding:8px">N. viaggi</th>
    </tr>
  </thead>
<tr style="background-color:white; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#1</td>
<td style="padding:8px">{}</td>""".format(origini[0] if len_check_origini > 0 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origini[0] if len_check_destinazioni > 0 else '//') + """
</tr>
<tr style="background-color:#F9FAFC; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#2</td>
<td style="padding:8px">{}</td>""".format(origini[1] if len_check_origini > 1 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origini[1] if len_check_origini > 1 else '//') + """
</tr>
<tr style="background-color:white; border-width: 0 1px 1px 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#3</td>
<td style="padding:8px">{}</td>""".format(origini[2] if len_check_origini > 2 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origini[2] if len_check_origini > 2 else '//') + """
</tr>
</table>
  </div>
</div>"""
        return html


    m = folium.Map(zoom_start=14, location=(45.467250, 9.189686),
                   tiles="https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZGVsZm8xIiwiYSI6ImNsbmx1YzB6MzJwNDgya3JsZzJsZjc1YWwifQ.6nVOkmTdDbEXbOPu3twfwA",
                   attr="Mapbox")
    m.get_root().html.add_child(folium.JavascriptLink('https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.min.js'))

    for index, row in locations.iterrows():
        selected_row = nil_milano[nil_milano['NIL'] == row['Partenza']]
        opaq = 100 * (row['conteggio'] / int(totale_viaggi))
        opaq = max(opaq_minima, opaq)
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

    for index1, row1 in nil_milano.iterrows():
        html = popup_html(index1)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Circle(location=[row1['quartieri_centroidi_X'], row1['quartieri_centroidi_Y']], color='black',
                      weight=0.6, fill_opacity=1, fill_color=[row1['colori']], radius=50, popup=popup).add_to(m)

    st.info("""La mappa mostra i centroidi dei Nuclei di Identità Locale (NIL) e le loro connessioni. I dati si riferiscono a un campione di viaggi effettuati nel luglio 2023 utilizzando servizi di car-sharing, biciclette, scooter e monopattini condivisi.
        """, icon="ℹ️")

    m.save("prova.html")
    HtmlFile = open("prova.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=600, scrolling=True)


def visualizza_mappa():
    st.title('Trajectory Flow Map')
    import plotly.express as px
    import geopandas as gpd

    st.info("""La trajectory flow map mostra il tracciato dei viaggi che hanno come origine o destinazione il NIL selezionato. I dati si riferiscono a un campione di viaggi effettuati nel luglio 2023 utilizzando servizi di car-sharing, biciclette, scooter e monopattini condivisi.
                    """, icon="ℹ️")

    df_milano = gpd.read_file('viaggi_milano_sample.csv')
    with st.sidebar:
        with st.form("my_form"):
            option = st.selectbox('Seleziona un NIL', (df_milano['Arrivo'].unique()), index=40)
            direzione = st.radio("Direzione dei flussi", ["Entrata", "Uscita"], index=0)
            data_inizio = datetime.date(2023, 7, 1)
            data_fine = datetime.date(2023, 7, 1)
            with st.expander("Intervallo di tempo"):
                date = st.date_input("Data", (data_inizio, data_fine), min_value=data_inizio, )
                time_start = st.time_input('Ora inizio', datetime.time(0, 0), )
                time_end = st.time_input('Ora fine', datetime.time(23, 59))
            stile_mappa = st.selectbox('Stile mappa', ['dark', 'light', 'satellite', 'open-street-map'], index=0)
            submitted = st.form_submit_button("Genera mappa")

    if submitted:
        if direzione == 'Entrata':
            flow = 'Arrivo'
        else:
            flow = 'Partenza'

        df_milano = df_milano[df_milano[flow] == option]

        date_time_start = datetime.datetime.combine(date[0], time_start)
        date_time_end = datetime.datetime.combine(date[1], time_end)

        df_milano['local_ts_start'] = pd.to_datetime(df_milano['local_ts_start'])
        df_milano['local_ts_end'] = pd.to_datetime(df_milano['local_ts_end'])
        df_milano = df_milano[
            (df_milano['local_ts_start'] >= date_time_start) & (df_milano['local_ts_end'] <= date_time_end)]
        df_milano['geom_wkt_estimated_route'] = df_milano['geom_wkt_estimated_route'].apply(loads)

        df_milano = gpd.GeoDataFrame(df_milano, geometry='geom_wkt_estimated_route', crs='EPSG:4326')
        exploded = df_milano.explode('geom_wkt_estimated_route')

        lats = []
        lons = []
        names = []
        vehicles = []
        for feature, name, vehicle in zip(exploded.geometry, exploded.id, exploded.type_vehicle):
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
                names = np.append(names, [name] * len(y))
                vehicles = np.append(vehicles, [vehicle] * len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
                vehicles = np.append(vehicles, None)

        newnames = {'C': 'Auto (C)', 'B': 'Bici (B)', 'M': 'Scooter (M)', 'S': 'Monopattini (S)'}

        fig = px.line_mapbox(lat=lats, lon=lons,
                             mapbox_style=stile_mappa, line_group=names, color=vehicles,
                             labels={'line_group': 'ID', 'color': 'Mezzo', }, )

        fig.update_layout(mapbox_zoom=10, legend_title_text='Mezzi di trasporto', height=634, legend=dict(
            yanchor="top",
            orientation='h',
            y=1.05,
            xanchor="left",
            x=0)
                          , margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,

            ))
        fig.update_mapboxes(
            accesstoken="pk.eyJ1IjoiZGVsZm8xIiwiYSI6ImNsbmx1YzB6MzJwNDgya3JsZzJsZjc1YWwifQ.6nVOkmTdDbEXbOPu3twfwA")
        fig.update_traces(opacity=0.6)

        fig.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        st.plotly_chart(fig, use_container_width=True, height=634)


def chord_diagram():
    st.title('Chord Diagram')

    # Create a context manager to run an event loop
    @contextmanager
    def setup_event_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            yield loop
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # Use the context manager to create an event loop
    with setup_event_loop() as loop:
        import holoviews as hv


    with st.sidebar:

        options = st.multiselect(
            'Quali veicoli vuoi visualizzare?',
            ['Bici', 'Auto', 'Monopattini', 'Scooter'],
            ['Bici', 'Auto', 'Monopattini', 'Scooter']

        )
        viaggi_min = st.slider('Numero minimo di viaggi tra due quartieri', 20, 75, 30)

    dictionary_opts = {
        'Bici': 'B',
        'Auto': 'C',
        'Monopattini': 'M',
        'Scooter': 'S'
    }
    lista_input = []

    for i in options:
        lista_input.append(dictionary_opts[i])

    hv.extension('bokeh')

    partenza_destinazione = pd.read_csv('nuovo_dataframe2.csv')
    partenza_destinazione = partenza_destinazione[partenza_destinazione['Partenza'] != partenza_destinazione['Arrivo']]

    filtered_df = partenza_destinazione[partenza_destinazione['Viaggi'] >= viaggi_min]

    filtered_df = filtered_df[filtered_df['type_vehicle'].isin(lista_input)]

    filtered_df = filtered_df.drop(columns='type_vehicle')

    filtered_df = filtered_df.groupby(['Partenza', 'Arrivo'])['Viaggi'].sum().reset_index()
    colonna_unique = set(filtered_df['Partenza'])
    colonna_unique.update(filtered_df['Arrivo'])
    colonna_unique = list(colonna_unique)

    with st.container():
        st.info("""Il diagramma fornisce una rappresentazione visiva delle connessioni tra i NIL. I dati si riferiscono a un campione di viaggi effettuati nel luglio 2023 utilizzando servizi di car-sharing, biciclette, scooter e monopattini condivisi.
                        """, icon="ℹ️")

    n = 0
    dizionario = {}
    for i in colonna_unique:
        dizionario[i] = n
        n += 1

    links = filtered_df.replace({'Partenza': dizionario,
                                 'Arrivo': dizionario})

    nodes = pd.DataFrame({'index': dizionario.values(), 'name': dizionario.keys()})

    # filtered_df.rename(columns={"Viaggi": "values"})

    theme = Theme(
        json={
            'attrs': {
                'figure': {

                    'border_fill_color': '#0F1116',

                },
            }
        })

    hv.renderer('bokeh').theme = theme

    nodes = hv.Dataset(nodes, 'index')

    chord = hv.Chord((links, nodes))
    tooltips = [('NIL', '@name')]

    hover = HoverTool(tooltips=tooltips)

    chord.opts(cmap='viridis', edge_cmap='viridis', edge_color="Partenza", labels="name", node_color="index",
               height=600, width=600, tools=[hover, 'tap'])

    hv.save(chord, 'fig.html')
    HtmlFile = open("fig.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()

    tab1, tab2, = st.tabs(["Chord Diagram", "Tabella viaggi filtrati"])

    with tab1:

        components.html("<style>:root {background-color: #0F1116;}</style>"+ source_code, height=600,)

    with tab2:

        st.dataframe(filtered_df)



page_names_to_funcs = {
    "Introduzione": introduzione,
    "OD Flow Map": print_map,
    "Trajectory Flow Map": visualizza_mappa,
    "Chord Diagram": chord_diagram,
}
selected_page = st.sidebar.selectbox("Seleziona una pagina", page_names_to_funcs.keys())

with st.sidebar:
    placeholder = st.empty()
    placeholder.write("""
                     #### Configurazione pagina corrente""")

page_names_to_funcs[selected_page]()
