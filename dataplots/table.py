from google.cloud import datastore
import plotly.graph_objs as go
from plotly.offline import plot

def data_table(kind='Sentiment_Details', ticker='WM US', industry=None, startmonth=None, endmonth=None):
    # Initialize the Datastore client
    client = datastore.Client()

    # Create a query to fetch entities from the Datastore
    query = client.query(kind=kind)
    query.order = ['CallDate']

    # Fetch the data
    try:
        entities = list(query.fetch())
    
    except:
        return 429
    
    # Prepare the data for plotting
    keyword_period_scores = {}

    # Filter entities after fetching
    filtered_entities = [e for e in entities if e['YahooTicker'] == ticker]

    for entity in filtered_entities:
        period = entity['Period']
        keyword = entity['Keyword']
        score = entity['Score']

        if keyword not in keyword_period_scores:
            keyword_period_scores[keyword] = {}

        if period in keyword_period_scores[keyword]:
            keyword_period_scores[keyword][period].append(score)
        else:
            keyword_period_scores[keyword][period] = [score]

    table_period = []
    table_scores = []
    table_keyword = []

    for keyword, period_scores in keyword_period_scores.items():
        unique_periods = sorted(period_scores.keys())
        average_scores = [sum(scores) / len(scores)
                        for scores in period_scores.values()]

        # Add each row to list
        table_period.extend(unique_periods)
        table_scores.extend(average_scores)

        i=1

        while i <= len(average_scores):
            table_keyword.append(keyword)
            i += 1
        
    table_keyword.sort()

    # Prepare the Plotly table
    fig = go.Figure(data=[go.Table( 
    header=dict(values=['Period', 'Score', 'Keyword'], align="left"), 
    cells=dict(values=[table_period, table_scores, table_keyword], align="left")) 
    ]) 

    # Return HTML div
    return plot(fig, include_plotlyjs=True, output_type='div')
