import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

from datetime import date

from something import drawGantt
from components import createGantt
from something import getInOrderOfLastAvailabe
from something import addStats

from components import createDyePanel

#Data for gantt and tables
inOrderDF = getInOrderOfLastAvailabe()
inOrderDF = addStats(inOrderDF)
representDF = inOrderDF.loc[:, inOrderDF.columns != 'id']


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#Page layout
app.layout = html.Div(
    #width=12,
    children=[
    html.H1(children='Dye Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    html.Div([
        dbc.Row( children =[
            dbc.Col(children=[
                dcc.Graph(
                    id='example-graph',
                    figure=createGantt()
                )],
            width=12)
        ]),
        html.Div([
            dbc.Row([
                dbc.Col(
                    id='kit-table',
                    children=[
                    dash_table.DataTable(
                            id='kitTable',
                            columns=[{"name": i, "id": i} for i in representDF.columns],
                            data=representDF.to_dict('records'),
                            style_cell={'textAlign': 'left'},
                            row_selectable='single')],
                    width=4
                ),
                dbc.Col(id='dye-table',
                        children=[dbc.Label("")],
                        width=4)
                ]
            )
        ])
    ])
])

#Callback to show dye list when kit selected
@app.callback(
    dash.dependencies.Output('dye-table', 'children'),
    [dash.dependencies.Input('kitTable', 'derived_virtual_data'),
     dash.dependencies. Input('kitTable', 'derived_virtual_selected_rows')])
def f(rows,selected_row_indices):
    #print("Callback")
    if(selected_row_indices is None):
        return html.Div(html.P("Nothing selected"),id="bla")
    if(len(selected_row_indices) == 0):
        return html.Div(html.P("Nothing selected"),id="bla")

    row = selected_row_indices[0]
    print(inOrderDF.iloc[row])

    kitName = inOrderDF.iloc[row][1]
    kitID = inOrderDF.iloc[row][0]

    #print(row)
    #print(row)
    #print(kitID)

    print("Creating kit panel...")
    return createDyePanel(kitID)





if __name__ == '__main__':
    app.run_server(debug=True)