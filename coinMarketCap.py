from urllib.request import urlopen
from datetime import datetime, timedelta
import pandas as pd
import json

def getTopByMarketCap(limit = 11):
    """Returts list of top cryptos by market cap"""
    url_of_list = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit={limit}&sortBy=market_cap&sortType=desc"
    response = urlopen(url_of_list)
    data_json = json.loads(response.read())

    #get only id and symbol from json
    toplist = [{key: crypto[key] for key in crypto.keys()
                & {'id', 'symbol'}} for crypto in data_json['data']['cryptoCurrencyList']]
    
    return toplist

def getCryptoDailyDetail(crypto_id, time_start, time_end):
    crypto_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={crypto_id}&convertId=2781&timeStart={time_start}&timeEnd={time_end}"

    response = urlopen(crypto_url)
    data_json = json.loads(response.read())
    
    qu = [q['quote'] for q in data_json['data']['quotes']]
    df = pd.DataFrame(qu)
    df.timestamp = pd.to_datetime(pd.to_datetime(df.timestamp).dt.date)
    return df.set_index('timestamp')

def getTopHistory(limit=11, days=90):
    """Returts dict of dataframes with history of top cryptos by market cap"""
    toplist = getTopByMarketCap(limit)
    
    timeEnd = int(datetime.today().timestamp()) #today
    timeStart = int((datetime.today() - timedelta(days=days)).timestamp()) #today substract given days

    dfs = {crypto['symbol'] : getCryptoDailyDetail(crypto['id'], timeStart, timeEnd) for crypto in toplist}

    return dfs


def getHourlyPrice(crypto_id):
    crypto_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={crypto_id}&range=3M"
    response = urlopen(crypto_url)
    data_json = json.loads(response.read())
    
    points = data_json['data']['points']
    qu = [[time, points[time]['v'][0]] for time in points]
    df = pd.DataFrame(qu, columns=['timestamp','price'])
    df.timestamp = pd.to_datetime(df.timestamp, unit='s')
    df = df.set_index('timestamp')
    
    return df

def getTopHourly(limit = 11):
    """Returts dict of dataframes with history of top cryptos by market cap"""
    toplist = getTopByMarketCap(limit)

    dfs = {crypto['symbol'] : getHourlyPrice(crypto['id']) for crypto in toplist}
    # cc = pd.concat(dfs,keys=[c['symbol'] for c in toplist], axis=1)

    return dfs