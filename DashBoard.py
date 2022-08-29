
#===================================
# import das bibliotecas

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

#===================================
# Manipulação do DataFrame


pd.set_option('display.precision', 2)

colunas = ['NU_INSCRICAO', 'TP_SEXO','SG_UF_PROVA',
               'NU_NOTA_REDACAO','NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT']

enem19 = pd.read_csv('MICRODADOS_ENEM_2019.csv', sep=';', encoding='ISO-8859-1', usecols=colunas).dropna()
enem20 = pd.read_csv('MICRODADOS_ENEM_2020.csv', sep=';', encoding='ISO-8859-1', usecols=colunas).dropna()
enem19.columns = ['N° INSCRICAO', 'SEXO', 'ESTADO', 'NOTA REDACAO', 'NOTA CN', 'NOTA CH', 'NOTA LC', 'NOTA MT']
enem20.columns = ['N° INSCRICAO', 'SEXO', 'ESTADO', 'NOTA REDACAO', 'NOTA CN', 'NOTA CH', 'NOTA LC', 'NOTA MT']

enem19['TOTAL'] = enem19['NOTA CN']+enem19['NOTA CH']+enem19['NOTA LC']+enem19['NOTA MT']+enem19['NOTA REDACAO']
enem19['MEDIA'] = enem19['TOTAL'] / 5
enem19['MEDIAM'] = enem19['TOTAL'] / 5
enem20['TOTAL'] = enem20['NOTA CN']+enem20['NOTA CH']+enem20['NOTA LC']+enem20['NOTA MT']+enem20['NOTA REDACAO']
enem20['MEDIA'] = enem20['TOTAL'] / 5
enem20['MEDIAM'] = enem20['TOTAL'] / 5

media19 = enem19
media19 = media19.groupby('ESTADO').agg({'MEDIA': 'mean', 'MEDIAM': 'max'})
media20 = enem20
media20 = media20.groupby('ESTADO').agg({'MEDIA': 'mean', 'MEDIAM': 'max'})
media19.reset_index(inplace=True)
media20.reset_index(inplace=True)

mapa_brasil = json.load(open("geojson/brazil_geo.json", 'r'))

opcoes = list((media19['ESTADO']))
opcoes.append('Todos os Estados')
opcoes[0] = opcoes[-1]
del(opcoes[-1])



#===================================
# Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

fig = px.choropleth_mapbox(media19, locations='ESTADO', color='MEDIA',
                          center={'lat': -16.95, 'lon': -47.78}, zoom=3,
                          geojson=mapa_brasil, color_continuous_scale='Redor', opacity=0.4,
                          hover_data={'MEDIA': True, 'MEDIA': True, 'MEDIAM': True})

fig.update_layout(
    paper_bgcolor='#242424',
    autosize=True,
    margin=go.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style='carto-darkmatter'
)

fig2 = go.Figure(layout={'template': 'plotly_dark'})
fig2.add_trace(go.Scatter(x=media19['ESTADO'], y=media19['MEDIA']))
fig2.update_layout(
    paper_bgcolor='#242424',
    plot_bgcolor='#242424',
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)


#===================================
# Layout

app.layout = dbc.Container(
    dbc.Row([
        
        dbc.Col([
            html.Div([
           
                html.Img(id='logo', src=app.get_asset_url("ifpb-1"), height=50),
                html.H5("Médias das notas do enem por estado"),
                dbc.Button('BRASIL', color='primary', id='location-button', size='lg')
        
        ], style={}),
            
            html.P("Informe qual estado na qual deseja ver a média:", style={"margin-top": "40px"}),
            
            html.Div(id='div-test', children=[
                dcc.Dropdown(
                    opcoes,
                    value='Todos os Estados',
                    id='lista-estados',
                    style={"margin-top": "10px"}
                )
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("2019"),
                            html.H3(style={"color": "#008000"}, id='media19-notas-text'),
                            html.Span("Maior média: "),
                            html.H5(id='estado19-escolhido-text'),
                        ])
                    ], color="light", outline=True, style={"margin-top": '10px',
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                                          "color": "#FFFFFF"})
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("2020"),
                            html.H3(style={"color": "#008000"}, id='media20-notas-text'),
                            html.Span("Maior média: "),
                            html.H5(id='estado20-escolhido-text'),
                        ])
                    ], color="light", outline=True, style={"margin-top": '10px',
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                                          "color": "#FFFFFF"})
                ], md=6),
            ]),
            
            html.P("Estado escolhido:", style={"margin-top": "40px"}),
            
            dcc.Graph(id='line-graph ', figure=fig2)
        ], md=5, style={'padding': '25px', 'background-color': '#242424'}),
        
        dbc.Col([
            dcc.Loading(
                id='loading-1',
                type='default',
                children=[
                    dcc.Graph(id='choropleth-map', figure=fig, style={'height': "100vh", 'margin-right': '10px'})
                ]
            )
            
        ], md=7)
    ])

, fluid=True)

#===================================
# funções
@app.callback(
    [
        Output('estado19-escolhido-text', 'children'),
        Output('estado20-escolhido-text', 'children'),
        Output('media20-notas-text', 'children'),
        Output('media19-notas-text', 'children'),    
    ],
    [Input('lista-estados', 'value'),Input('location-button', 'children') ]
)
def display_status(value, location):
    if value == 'Todos os Estados': 
        es19 = 2019
        es20 = 2020
        m19 = '--'
        m20 = '--'        
    else:
        m19 = media19[media19['ESTADO']==value].iat[0,1]
        m19 = round(m19, 2)
        m20 = media20[media20['ESTADO']==value].iat[0,1]
        m20 = round(m20, 2)
        es19 = media19[media19['ESTADO']==value].iat[0,2]
        es19 = round(es19, 2)
        es20 = media20[media20['ESTADO']==value].iat[0,2]
        es20 = round(es20, 2)
    return (es19, es20, m20, m19)

#===================================
# Ligar Dash

if __name__ == "__main__":
    app.run_server(debug=False)