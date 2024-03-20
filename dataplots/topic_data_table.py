"""DASH FILE"""

from dash import dash_table, dcc, html, Input, Output, State, callback

def topic_data_table(topicdashapp):

    columns = ["Sector", "Classification", "Keyword"]

    topicdashapp.layout = html.Div([

        dash_table.DataTable(
            id='topic-data-table',
            columns=[{
                'name': '{}'.format(i),
                'id': 'column-{}'.format(i),
                'deletable': False,
                'renamable': False
            } for i in columns],
            data=[
                {'column-{}'.format(i): (j + (i-1)*5) for i in range(1, 5)}
                for j in range(5)
            ],
            editable=True,
            row_deletable=True,
            fixed_rows={'headers': True}, 
            style_table={'height': 400}
        ),

        html.Button('Add Topic', id='topic-add-button', n_clicks=0),
        html.Button('Revert', id='topic-cancel-button', n_clicks=0),
        html.Button('Save', id='topic-save-button', n_clicks=0),
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
