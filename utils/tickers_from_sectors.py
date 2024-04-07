import os, sys
root_path = os.path.abspath('..')
sys.path.append(root_path)

from settings import kindCompanyInfo

from google.cloud import datastore

def tickers_from_sectors(client: datastore.Client, sectors:list) -> list:
    client.query(kind=kindCompanyInfo)

    return