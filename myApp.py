#Dash and flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Output
from dash.dependencies import Input
from dash.dependencies import State

from flask import request

#Other
import re

#Project
from components import createGantt
from components import createDyePanel
from components import createTable
from components import createPersonalDyePanel
from components import createPersonalKitPanel

from dataManager import neverInBlc
from dataManager import access

from something import getInOrderOfLastAvailabe
from something import addStats
from something import goldFromInteger

from api_calls import check_api_key

#TODO: For deploy
#import sys
#print(sys.executable)

#APP
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#Some callback Inputs/Output components (ids) don't exist yet as they are created based on API key
app.config['suppress_callback_exceptions'] = True

#Data for gantt and tables
inOrderDF = getInOrderOfLastAvailabe()
inOrderDF = addStats(inOrderDF)
representDF = inOrderDF.loc[:, inOrderDF.columns != 'id']

notInBlc = ""
for x, y in neverInBlc():
    notInBlc = notInBlc + y + ", "
notInBlc = notInBlc[:-2]

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

        #API key text are and button
        dbc.Row([
            dbc.Col([],width=1),
            dbc.Col(
                [dbc.Input(id="apiField", placeholder="API KEY", type="text")],
                width=5
            ),
            dbc.Col(
                [dbc.Button("Enter API", id="apiButton")],
                width=1
            )
        ]),

        #Meta card:
        # Displays API key used (when valid entered), total sell value, total buy value

        dbc.Spinner([
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
                outline=True),
        ]),

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
        #Invalid key toast
        dbc.Toast(
            "Check your key",
            id="invalid-toast",
            className="mb-0",
            header="Invalid API key",
            is_open=False,
            dismissable=True,
            icon="danger",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            duration=3000,
        )
    ])

    return content

#MAIN LAYOUT DEFINITON
# Calls functions to make subcomponents
app.layout = html.Div(
    #width=12,
    children=[
    html.H1(children='DYE DASH'),
    dbc.Tabs([
        dbc.Tab(tab1content(),label="AVAILABILITY CHART"),
        dbc.Tab(tab2content(), label="BASIC INFORMATION"),
        dbc.Tab(tab3content(),label="PORTFOLIO")
    ]),

    html.Div([""],id='api-store',style={'display':'none'}),
])


#@app.callback(
#    Output("loading-output", "children"), [Input("apiButton", "n_clicks")]
#)
#def load_output(n):
#    if n:
#        #time.sleep(1)
#        return f"Output loaded {n} times"
#    return "Output not reloaded yet"

#Creates a PERSONAL KIT panel when a valid API key is entered
# Saves api to hiden div (id:api-store) for later use
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

    #Check api key validity
    isValid = check_api_key(apiKey)
    if not isValid:
        print("[%s] Invalid api key"%request.remote_addr)
        return [dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update, True]

    #Access
    access(apiKey)

    print("[%s] Creating personal kit panel..."%request.remote_addr)

    #Creating the dash component
    panelComponent = createPersonalKitPanel(apiKey)

    #Totaling the values of all kit, displayed on top
    data = panelComponent.data

    totalSell = 0
    totalBuy = 0
    for each in data:
        totalSell += int(re.sub("[^0-9]", "",each['Sell value']))
        totalBuy += int(re.sub("[^0-9]", "" ,each['Buy value']))

    return [panelComponent,apiKey, {'display':'inline'}, ["Using: %s"%apiKey],
            ["Portfolio sell value: %s"%goldFromInteger(totalSell),html.Br(),"Portfolio buy value: %s"%goldFromInteger(totalBuy)], False]

#Creates a PERSONAL DYE PANEL when row in kit table is selected
@app.callback(
    Output('personal-dyes', 'children'),
    [Input('personalKitTable', 'derived_virtual_selected_rows'),
     Input('api-store', 'children')])
def personalDyes(selected_row_indices, apiKey):
    if(selected_row_indices is None):
        return html.Div(html.P("Nothing selected"),id="bla")
    if(len(selected_row_indices) == 0):
        return html.Div(html.P("Nothing selected"),id="bla")

    row = selected_row_indices[0]
    kitName = inOrderDF.iloc[row][1]
    kitID = inOrderDF.iloc[row][0]

    print("[%s] Opening personal panel..."%request.remote_addr)
    return createPersonalDyePanel(kitID, apiKey)

#Creates a BASIC DYE PANEL when a kit table row is selected
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
    kitName = inOrderDF.iloc[row][1]
    kitID = inOrderDF.iloc[row][0]

    print("[%s] Creating dye panel..."%request.remote_addr)
    return createDyePanel(kitID)

if __name__ == '__main__':
    #app.run(host= ‘0.0.0.0’)
    app.run_server(debug=True)