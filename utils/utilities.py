import datetime

from settings import kindCOMPANYINFO

from utils.gcp.datastore import queryEntities

def tickers_from_sectors(sectors:list) -> list:

    results = queryEntities(kind=kindCOMPANYINFO, filters=[{'property_name':'Sector', 'operator':'IN', 'value':sectors}])

    output = []

    for entity in results:
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



def get_tickers() -> list:

    results = queryEntities(kind='Company_Info', order="Yahoo_Ticker")
    
    output = []
    
    for entity in results:
        output.append(entity["Yahoo_Ticker"])

    return output

def getDateTime():
    current_time = datetime.datetime.now()

    return str(current_time.year) + '_' + str(current_time.month) + '_' + str(current_time.day) + '-' + str(current_time.hour) + '_' + str(current_time.minute)