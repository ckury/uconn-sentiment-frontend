from settings import kindCOMPANYINFO

from google.cloud import datastore

def tickers_from_sectors(client: datastore.Client, sectors:list) -> list:
    query = client.query(kind=kindCOMPANYINFO)
    query.add_filter(property_name='Sector', operator='IN', value=sectors)

    entities = query.fetch()

    output = []

    for entity in entities:
        output.append(entity["Yahoo_Ticker"])

    return output

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

def title_creation(tickers, sectors, weighted):
    output = ""

    if weighted is True: output += 'Weighted '
    if weighted is False: output += 'Unweighted '
    
    output += "Sentiment Scores Over Time Including "

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