"""DASH FILE"""

from google.cloud import datastore
from dash import dash_table, dcc, html, Input, Output, State, callback

def view_data_table(datadashapp, kind='Banks', ticker='JPM US', industry=None, startmonth=None, endmonth=None):

    client = datastore.Client()

    query = client.query(kind=kind)

    entities = list(query.fetch())

    columns = [{'id': "Period", 'name': "Period"}, {'id':"Keyword", 'name': "Keyword"}, {'id':"Score", 'name':"Score"}]

    data_values = []

    for entity in entities:
        data_values.append({"Period": entity.get('Period'), "Keyword": entity.get('Keyword'), "Score": entity.get('Score')})

    datadashapp.layout = html.Div([

        dash_table.DataTable(
            id='view-data-table',
            columns=columns,
            data=data_values,
            editable=False,
            row_deletable=False,
            row_selectable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True},
            style_table={'height': "100%"}
        )
    ])