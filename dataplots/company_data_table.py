"""DASH FILE"""

from google.cloud import datastore
from dash import dash_table, dcc, html, Input, Output, State, callback

from settings import kindCOMPANYINFO

def company_data_table(companydashapp):

    client = datastore.Client()

    query = client.query(kind=kindCOMPANYINFO)

    try:
        entities = list(query.fetch())
    
    except:
        entities = []

    columns = [{'id':"Yahoo_Ticker", 'name':"Yahoo Ticker"}, {'id': "Sector", 'name': "Sector"}, {'id':"Full_Name", 'name': "Full Name"}]

    data_values = []

    for entity in entities:
        data_values.append({"Sector": entity.get('Sector'), "Full_Name": entity.get('Full_Name'), "Yahoo_Ticker": entity.get('Yahoo_Ticker')})

    companydashapp.layout = html.Div([

        dash_table.DataTable(
            id='company-data-table',
            columns=columns,
            data=data_values,
            editable=True,
            row_deletable=True,
            fixed_rows={'headers': True}, 
            style_table={'height': 400}
        ),

        html.Button('Add Company', id='company-add-button', n_clicks=0),
    ])


    @callback(
        Output('company-data-table', 'data'),
        Input('company-add-button', 'n_clicks'),
        State('company-data-table', 'data'),
        State('company-data-table', 'columns'))
    def add_row(n_clicks, rows, columns):
        if n_clicks > 0:
            rows.append({c['id']: '' for c in columns})
        return rows
