from urllib.request import urlopen
from datetime import datetime, timedelta
import pandas as pd
import json

def getTopHistory(limit=10, days=90):
    """Returts dict of dataframes with history of top cryptos by market cap"""
    url_of_list = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit={limit}&sortBy=market_cap&sortType=desc"
    response = urlopen(url_of_list)
    data_json = json.loads(response.read())

    #get only id and symbol from json
    top10list = [{key: crypto[key] for key in crypto.keys()
                & {'id', 'symbol'}} for crypto in data_json['data']['cryptoCurrencyList']]
    
    timeEnd = int(datetime.today().timestamp()) #today
    timeStart = int((datetime.today() - timedelta(days=days)).timestamp()) #today substract 90 days

    dfs = {}
    for crypto in top10list:
        crypto_id = crypto['id']

        crypto_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={crypto_id}&convertId=2781&timeStart={timeStart}&timeEnd={timeEnd}"

        response = urlopen(crypto_url)
        data_json = json.loads(response.read())
        
        qu = [q['quote'] for q in data_json['data']['quotes']]
        df = pd.DataFrame(qu)
        df.timestamp = pd.to_datetime(df.timestamp)
        dfs[crypto['symbol']] = df

    return dfs