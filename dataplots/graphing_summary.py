import os, sys
root_path = os.path.abspath('..')
sys.path.append(root_path)

from google.cloud import datastore
import plotly.graph_objs as go
from plotly.offline import plot
from utils.tickers_from_sectors import tickers_from_sectors

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
    
    # Initialize Datastore Client
    client = datastore.Client()

    # Converting string provided by URL to boolean value
    if weighted in [True, "True"]: weighted = True; scoreColumn = "Weighted Average"
    if weighted in [False, "False"]: weighted = False; scoreColumn = "Total Average"

    # Cleanup tickers and sectors and put them in correct format
    clean_tickers = input_cleanup(ticker)
    clean_sectors = input_cleanup(sector)

    # Try to fetch the data
    try:
        entities = fetch_ticker_data(client=client, kind="Banks_Summary")

    # If data fetch fails, return catch error and provide error code as response
    except:
        return 429

    # Filter entities after fetching
    if "BANKS" in clean_sectors: # TODO: Currently this is a temporary workaround, This should be switched to querying for tickers in the sector using the tickers_from_sectors function imported
        filtered_entities = entities
    else:
        filtered_entities = [e for e in entities if e['Yahoo Ticker'] in clean_tickers]

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

def input_cleanup(input: str | list) -> list:
    '''
    This function takes an input string gathered from a URL and removes unnessesary spaces, separates tickers by comma and returns them as list.\n
    If list is provided, processing is ignored and original list is returned
    '''

    if input is list:
        return input

    output = []

    # Multiple tickers separated and cleaned up
    if "," in input:
        input = input.split(",")
        for i in input:
            output.append(i.strip().upper())

    # Single ticker cleaned up
    else:
        output.append(input.strip().upper())
    
    return output

def title_creation(tickers: list, sectors: list, weighted: bool) -> str: 
    output = ""

    if weighted is True: output += 'Weighted '
    if weighted is False: output += 'Unweighted '
    
    output += "Summary Sentiment Scores Over Time Including "

    if '' not in tickers:
        output += "Tickers: "
        for t in tickers:
            output += t
            output += ', '
        
        output = output[:-2]
        if '' not in sectors:
            output += " and "

    if '' not in sectors:
        output += "Sectors: "
        for s in sectors:
            output += s
            output += ', '
        output = output[:-2]

    return output

def fetch_ticker_data(client: datastore.Client, kind: str) -> list:
    # Create a query to fetch entities from the Datastore
    query = client.query(kind=kind)
    query.order = ['Yahoo Ticker']
    
    # Return a list of the entities
    return list(query.fetch())

def prepare_period(input: str) -> str:
    '''
    This function outputs period in the form of YYYYQQ whether input is QQYYYY or YYYYQQ
    '''
    if input[0] == "Q":
        quarter = input[1]
        output = input[2:]

        output += "Q" + quarter

    else:
        output = input

    return output