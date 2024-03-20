"""DASH FILE"""

from dash import dash_table, dcc, html, Input, Output, State, callback

def company_data_table(dashapp):

    columns = ["Company Long Name", "Yahoo Ticker", "Industry"]

    dashapp.layout = html.Div([

        dash_table.DataTable(
            id='adding-rows-table',
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
            row_deletable=True
        ),

        html.Button('Add Company', id='editing-rows-button', n_clicks=0),
    ])


    @callback(
        Output('adding-rows-table', 'data'),
        Input('editing-rows-button', 'n_clicks'),
        State('adding-rows-table', 'data'),
        State('adding-rows-table', 'columns'))
    def add_row(n_clicks, rows, columns):
        if n_clicks > 0:
            rows.append({c['id']: '' for c in columns})
        return rows
