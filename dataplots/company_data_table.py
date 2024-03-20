"""DASH FILE"""

from dash import dash_table, dcc, html, Input, Output, State, callback

def company_data_table(companydashapp):

    columns = ["Company Long Name", "Yahoo Ticker", "Industry"]

    companydashapp.layout = html.Div([

        dash_table.DataTable(
            id='company-data-table',
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
