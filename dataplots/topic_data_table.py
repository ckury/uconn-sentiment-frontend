"""DASH FILE"""

from google.cloud import datastore
from dash import dash_table, dcc, html, Input, Output, State, callback

def topic_data_table(topicdashapp):

    client = datastore.Client()

    query = client.query(kind="Topics")

    entities = list(query.fetch())

    columns = [{'id': "Sector", 'name': "Sector"}, {'id':"Classification", 'name': "Classification"}, {'id':"Keyword", 'name':"Keyword"}]

    data_values = []

    data_values.append({"Sector": "Test Sector", "Classification": "Test Classification", "Keyword": "Test Keyword"})

    for entity in entities:
        data_values.append({"Sector": entity.get('Sector'), "Classification": entity.get('classification'), "Keyword": entity.get('keyword')})

    topicdashapp.layout = html.Div([

        dash_table.DataTable(
            id='topic-data-table',
            columns=columns,
            data=data_values,
            editable=True,
            row_deletable=True,
            fixed_rows={'headers': True}, 
            style_table={'height': 400}
        ),

        html.Button('Add Topic', id='topic-add-button', n_clicks=0),
    ])


    @callback(
        Output('topic-data-table', 'data'),
        Input('topic-add-button', 'n_clicks'),
        State('topic-data-table', 'data'),
        State('topic-data-table', 'columns'))
    def add_row(n_clicks, rows, columns):
        if n_clicks > 0:
            rows.append({c['id']: '' for c in columns})
        return rows
