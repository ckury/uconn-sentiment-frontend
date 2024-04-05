from google.cloud import datastore
import plotly.graph_objs as go
from plotly.offline import plot

def data_plot_summary(ticker=None, sector=None, weighted="False", startmonth=None, endmonth=None):
    # Prepare the Plotly graph
    fig = go.Figure()
    
    # Initialize Datastore Client
    client = datastore.Client()

    # Converting string provided by URL to boolean value
    if weighted == "True": weighted = True; scoreColumn = "Weighted Average"
    if weighted == "False": weighted = False; scoreColumn = "Total Average"

    # Cleanup tickers and sectors and put them in correct format
    clean_tickers = input_cleanup(ticker)
    clean_sectors = input_cleanup(sector)

    # Try to fetch the data
    try:
        entities = fetch_data(client=client, kind="Banks_Summary")

    # If data fetch fails, return error code
    except:
        return 429

    # Filter entities after fetching
    if "BANKS" in clean_sectors:
        filtered_entities = entities
    else:
        filtered_entities = [e for e in entities if e['Yahoo Ticker'] in clean_tickers]

    scoreDictionary = {}

    for entity in filtered_entities:
        period = prepare_period(entity['Period'])
        tickerTrace = entity['Yahoo Ticker']
        score = entity[scoreColumn]

        if tickerTrace in scoreDictionary:
            scoreDictionary[tickerTrace].append((period, score))
        else:
            scoreDictionary[tickerTrace] = [(period, score)]


    

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
        
    fig.update_layout(
        title=title_creation(clean_tickers, clean_sectors, weighted),
        xaxis_title='Period',
        yaxis_title='Sentiment Score',
        legend_title='Legend',
        xaxis=dict(tickangle=45),
        yaxis_range=[-1, 1]
    )

    # Return HTML div
    return plot(fig, include_plotlyjs=True, output_type='div')

def input_cleanup(input):
    # Cleaning up the tickers and putting them into a list
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

def title_creation(tickers, sectors, weighted):
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

def fetch_data(client, kind):
    # Create a query to fetch entities from the Datastore
    query = client.query(kind=kind)
    query.order = ['Yahoo Ticker']
    
    # Return a list of the entities
    return list(query.fetch())

def prepare_period(input):
    if input[0] == "Q":
        quarter = input[1]
        output = input[2:]

        output += "Q" + quarter

    else:
        output = input

    return output

def tickers_from_sectors(client, sector):
    return