import plotly.graph_objs as go
from plotly.offline import plot
from utils.utilities import input_cleanup, title_creation, tickers_from_sectors, prepare_period
from utils.gcp.datastore import queryEntities

def data_plot_summary(ticker: str | list=None,
                      sector: str | list=None, 
                      weighted: str | bool=False, 
                      startmonth=None, 
                      endmonth=None) -> str:
    '''
    This function takes in tickers and/or sectors with filtering options and returns a graph HTML div in the form of a str \n
    Note: This graph pulls from summary data kind in GCP and displays each ticker as a separate trace on graph. The sectors 
    are flattened into individual tickers and are displayed as if they were inputted individually
    '''

    # Initialize plotly graph instance
    fig = go.Figure()

    # Converting string provided by URL to boolean value
    if weighted in [True, "True"]: weighted = True; scoreColumn = "Weighted Average"
    if weighted in [False, "False"]: weighted = False; scoreColumn = "Total Average"

    # Cleanup tickers and sectors and put them in correct format
    clean_tickers = input_cleanup(ticker)
    clean_sectors = input_cleanup(sector)

    tickerfilterlist = []

    tickerfilterlist.extend(clean_tickers)
    tickerfilterlist.extend(tickers_from_sectors(sectors=clean_sectors))

    # Try to fetch the data
    try:
        entities = queryEntities(kind="Sentiment_Summary", order='YahooTicker')

    # If data fetch fails, return catch error and provide error code as response
    except:
        return 429

    # Filter entities after fetching
    filtered_entities = [e for e in entities if e['Yahoo Ticker'] in tickerfilterlist]

    # Query entity disection and data arrangement preparation for adding trace to graph. This takes rows and consolidating them into a dictionary with the tickers as kinds.

    scoreDictionary = {}

    for entity in filtered_entities:
        period = prepare_period(entity['Period'])
        tickerTrace = entity['Yahoo Ticker']
        score = entity[scoreColumn]

        if tickerTrace in scoreDictionary:
            scoreDictionary[tickerTrace].append((period, score))
        else:
            scoreDictionary[tickerTrace] = [(period, score)]


    # Take data out of dictionary and plot trace

    for tickerTrace, data in scoreDictionary.items():
        periods = []
        scores = []

        data.sort()

        for period, score in data:
            periods.append(period)
            scores.append(score)

        fig.add_trace(go.Scatter(
            x=periods,
            y=scores,
            mode='lines+markers',
            name=tickerTrace
        ))

    # Add layout configurations to the graph
        
    fig.update_layout(
        title=title_creation(clean_tickers, clean_sectors, weighted),
        xaxis_title='Period',
        yaxis_title='Sentiment Score',
        legend_title='Legend',
        xaxis=dict(tickangle=45),
        yaxis_range=[-1, 1]
    )

    # Return HTML div to main flask app
    return plot(fig, include_plotlyjs=True, output_type='div')
