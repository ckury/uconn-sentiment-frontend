from google.cloud import datastore
import plotly.graph_objs as go
from plotly.offline import plot

def data_plot(kind='Sentiment_Details', ticker='TEP FP'):
    # Initialize the Datastore client
    client = datastore.Client()

    # Create a query to fetch entities from the Datastore
    query = client.query(kind=kind)
    query.order = ['CallDate']

    # Fetch the data
    entities = list(query.fetch())

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

    # Prepare the Plotly graph
    fig = go.Figure()

    for keyword, period_scores in keyword_period_scores.items():
        unique_periods = sorted(period_scores.keys())
        average_scores = [sum(scores) / len(scores)
                        for scores in period_scores.values()]

        # Create a trace for each keyword
        fig.add_trace(go.Scatter(
            x=unique_periods,
            y=average_scores,
            mode='lines+markers',
            name=keyword
        ))

    fig.update_layout(
        title='Average Sentiment Scores Over Time by Keyword for YahooTicker TEP FP',
        xaxis_title='Period',
        yaxis_title='Average Sentiment Score',
        legend_title='Keywords',
        xaxis=dict(tickangle=45)
    )

    # Return HTML div
    return plot(fig, include_plotlyjs=True, output_type='div')
