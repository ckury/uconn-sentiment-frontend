"""DASH FILE"""

from google.cloud import datastore
from dash import dash_table, dcc, html, Input, Output, State, callback

def keyword_data_table(topicdashapp):

    client = datastore.Client()

    query = client.query(kind="Topics")

    try:
        entities = list(query.fetch())
    
    except:
        entities = []

    columns = [{'id':"Keyword", 'name':"Keyword"}, {'id':"Category", 'name': "Category"}]

    data_values = []

    for entity in entities:
        data_values.append({"Keyword": entity.get('Keyword'), "Category": entity.get('Category')})

    topicdashapp.layout = html.Div([

        dash_table.DataTable(
            id='topic-data-table',
            columns=columns,
            data=data_values,
            editable=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True}, 
            style_table={'height': "100%"}
        ),

        html.Button('Add Topic Entry to Bottom', id='topic-add-button', n_clicks=0),
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
