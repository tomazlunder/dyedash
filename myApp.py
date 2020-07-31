import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

from dash.dependencies import Output
from dash.dependencies import Input
from dash.dependencies import State

from datetime import date

from something import drawGantt
from components import createGantt
from something import getInOrderOfLastAvailabe
from something import addStats

from components import createDyePanel
from components import createTable
from components import createPersonalDyePanel

from components import createPersonalKitPanel

from api_calls import findOwnedDyes
from api_calls import check_api_key

from dataManager import neverInBlc

from something import goldFromInteger

from dataManager import access

#Data for gantt and tables
inOrderDF = getInOrderOfLastAvailabe()
inOrderDF = addStats(inOrderDF)
representDF = inOrderDF.loc[:, inOrderDF.columns != 'id']

notInBlc = ""
for x, y in neverInBlc():
    notInBlc = notInBlc + y + ", "
notInBlc = notInBlc[:-2]

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.config['suppress_callback_exceptions'] = True

def tab1content():
    content = html.Div([
        html.Center(html.H2("Availability chart")),
        html.Div(children =[
            dbc.Col(children=[
                dcc.Graph(
                    id='example-graph',
                    figure=createGantt()
                )],
            width=12)
        ]),
        html.Center(html.Label("Never in Black Lion Chest: %s" % str(notInBlc), style={'margin-right': '20'}))
    ])

    return content

def tab2content():
    content = html.Div([
        html.Center(html.H2("Kit&Dye Information")),
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    id='kit-table',
                    children=[
                    createTable(representDF,'kitTable')]
                ),
                dbc.Col(id='dye-table',
                        children=[dbc.Label("")],
                        #width=4
                    )
                ]
            )
        ])
    ])

    return content

def tab2content2():
    content = html.Div([
        html.Center(html.H2("Kit&Dye Information")),
        html.Div(
            id="basic-div",
            children=[
                dbc.CardDeck([
                    dbc.Card([
                        dbc.CardBody(
                            id='kit-table',
                            className='card-text',
                            children=[
                                createTable(representDF, 'kitTable')],
                            # width=4
                        )],
                        style={"min-width": "600px"},
                        color="success",
                        outline=True
                    ),
                    dbc.Card([
                        dbc.CardBody(
                            id='dye-table',
                            children=[dbc.Label("")],
                            # width=4
                        )],
                        style={"min-width": "600px"},
                        color="success",
                        outline=True
                    )
                ],
                )
            ]
        )
    ])

    return content

def tab3content():
    content = html.Div([
        html.Center(html.H2("Portfolio")),
        dbc.Row([
            dbc.Col([],width=1),
            dbc.Col(
                [dbc.Input(id="apiField", placeholder="API KEY", type="text")],
                width=5
            ),
            dbc.Col(
                [dbc.Button("Enter API", id="apiButton")],
                width=1
            ),
        ]),

        dbc.Card([
            dbc.CardBody([
                dbc.Col([],
                    id="valid_api_div",
                    style={'font-size': '16px'}),

                dbc.Col([],
                    id="total-out",
                    style={'font-size': '16px'})
                ])
            ],
            outline=True)
        ,

        html.Br(),
        html.Div(
            id = "personal-div",
            style={'display':'none'},
            children = [
                dbc.CardDeck([
                    dbc.Card([
                        dbc.CardBody(
                            id='personal-kits',
                            className= 'card-text',
                            children=[dbc.Label("")],
                            # width=4
                        )],
                    style={"min-width": "870px"},
                    color="success",
                    outline=True
                    ),
                    dbc.Card([
                        dbc.CardBody(
                            id='personal-dyes',
                            children=[dbc.Label("")],
                            # width=4
                        )],
                        style={"min-width": "700px"},
                        color="success",
                        outline=True
                    )
                ],
                )
            ]
        ),
        dbc.Toast(
            "Check your key",
            id="invalid-toast",
            className="mb-0",
            header="Invalid API key",
            is_open=False,
            dismissable=True,
            icon="danger",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            duration=3000,
        )
    ])


    return content

#Page layout
app.layout = html.Div(
    #width=12,
    children=[
    html.H1(children='DYE DASH'),
    dbc.Tabs([
        dbc.Tab(tab1content(),label="AVAILABILITY CHART"),
        dbc.Tab(tab2content2(),label="BASIC INFORMATION"),
        dbc.Tab(tab3content(),label="PORTFOLIO")
    ]),

    html.Div([""],id='api-store',style={'display':'none'}),
])

#OPEN PERSONAL KIT LIST
#Saves api to hiden div (id:api-store)
@app.callback([Output('personal-kits', 'children'),
               Output('api-store', 'children'),
               Output('personal-div', 'style'),
               Output('valid_api_div','children'),
               Output('total-out','children'),
               Output('invalid-toast','is_open')],
              [Input('apiButton', 'n_clicks')],
              [State('apiField', 'value')])
def personalKits(n_clicks, apiKey):
    #This is called one time on initialization, skip that call
    if n_clicks is None:
        return [dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update, False]

    print("API BUTTON CLICKED")

    #Check api key validity
    isValid = check_api_key(apiKey)
    if not isValid:
        print("Invalid api key")
        return [dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update, True]

    access(apiKey)

    b = createPersonalKitPanel(apiKey)

    a = findOwnedDyes(apiKey)
    totalSell = a['num'] * a['sell']
    totalSell = sum(totalSell)

    totalBuy = a['num'] * a['buy']
    totalBuy = sum(totalBuy)

    return [b,apiKey, {'display':'inline'}, ["Using: %s"%apiKey],
            ["Portfolio sell value: %s"%goldFromInteger(totalSell),html.Br(),"Portfolio buy value: %s"%goldFromInteger(totalBuy)], False]

#OPEN PERSONAL DYE LIST
# Input('personalKitTable', 'derived_virtual_data') - not needed, here just in case
@app.callback(
    Output('personal-dyes', 'children'),
    [Input('personalKitTable', 'derived_virtual_selected_rows'),
     Input('api-store', 'children')])
def personalDyes(selected_row_indices, apiKey):
    print("Api key: %s"%apiKey)
    #print("Callback")
    if(selected_row_indices is None):
        return html.Div(html.P("Nothing selected"),id="bla")
    if(len(selected_row_indices) == 0):
        return html.Div(html.P("Nothing selected"),id="bla")

    row = selected_row_indices[0]
    #print(inOrderDF.iloc[row])

    kitName = inOrderDF.iloc[row][1]
    kitID = inOrderDF.iloc[row][0]

    dfOwned = findOwnedDyes(apiKey)

    print("Creating kit panel...")
    return createPersonalDyePanel(kitID, dfOwned)

#OPEN DYE LIST
@app.callback(
    Output('dye-table', 'children'),
    [Input('kitTable', 'derived_virtual_selected_rows')])
def dyes(selected_row_indices):
    #print("Callback")
    if(selected_row_indices is None):
        return html.Div(html.P("Nothing selected"),id="bla")
    if(len(selected_row_indices) == 0):
        return html.Div(html.P("Nothing selected"),id="bla")

    row = selected_row_indices[0]
    #print(inOrderDF.iloc[row])

    kitName = inOrderDF.iloc[row][1]
    kitID = inOrderDF.iloc[row][0]

    #print(row)
    #print(row)
    #print(kitID)

    print("Creating dye panel...")
    return createDyePanel(kitID)

if __name__ == '__main__':
    #app.run(host= ‘0.0.0.0’)
    app.run_server(debug=True)