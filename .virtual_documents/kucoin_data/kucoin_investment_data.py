### Investment data
#Real investment kucoin investment data 
#Initialize investments.ipynb file in Resources folder.
# Prepare API calls for investment data collection.
# Pull investment data from first exchange.
# Organize investment data.
# Pull investment data from remaining exchanges.
# Organize investment data from remaining exchanges


import datetime
import time
import base64
import hmac
import hashlib
import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os


%matplotlib inline

# silence warnings
import warnings
warnings.filterwarnings('ignore')


dotenv_path = 'C:/Desktop/my_gitrepos/project-2/kucoin_data/k.env'
load_dotenv(dotenv_path)


api_key = os.getenv('KUCOIN_api_key')
api_secret = os.getenv('KUCOIN_api_secret')
api_passphrase = os.getenv('KUCOIN_api_passphrase')


def get_headers(url, method):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + method + url
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }
    return headers

def get_account_balance():
    url = '/api/v1/accounts'
    headers = get_headers(url, 'GET')
    response = requests.get('https://api.kucoin.com' + url, headers=headers)
    if response.status_code == 200:
        balances = response.json()['data']
        return balances
    else:
        print('Failed to get account balances. Error code:', response.status_code)
        return None


get_account_balance()


balances = get_account_balance()
df = pd.DataFrame(balances)
account_data= df[['currency', 'balance', 'available','holds']]
account_data.head()


account_data.head()


def get_ticker(symbol):
    url = f'/api/v1/market/orderbook/level1?symbol={symbol}'
    headers = get_headers(url, 'GET')
    response = requests.get('https://api.kucoin.com' + url, headers=headers)
    if response.status_code == 200:
        ticker_data = response.json()
        return ticker_data['data']
    else:
        print('Failed to get ticker data for symbol', symbol, '. Error code:', response.status_code)
        return None


get_ticker('KNC-USDT')


def get_all_tickers():
    url = '/api/v1/market/allTickers'
    headers = get_headers(url, 'GET')
    response = requests.get('https://api.kucoin.com' + url, headers=headers)
    if response.status_code == 200:
        ticker_data = json.loads(response.text)
        return ticker_data
    else:
        print('Failed to get ticker data. Error code:', response.status_code)


#get_all_tickers()


def get_symbols():
    url = '/api/v2/symbols'
    headers = get_headers(url, 'GET')
    response = requests.request('get', 'https://api.kucoin.com'+url, headers=headers)
    if response.status_code == 200:
        symbols_data = response.json()['data']
        symbols_df = pd.DataFrame(symbols_data)
        return symbols_df
    else:
        print('Failed to get symbols data. Error code:', response.status_code)       


get_symbols()


def clean_symbols_data(symbols_df):
    symbols_df = symbols_df.loc[:, ['symbol', 'name', 'baseCurrency', 'quoteCurrency', 'feeCurrency', 'market']]
    symbols_df = symbols_df.rename(columns={
        'baseCurrency': 'base_currency',
        'quoteCurrency': 'quote_currency',
        'feeCurrency': 'fee_currency',
    })
    symbols_df = symbols_df.set_index('symbol')
    return symbols_df
symbols_df = get_symbols()
symbols_cleaned_df = clean_symbols_data(symbols_df)
symbols_cleaned_df.head()
symbols_cleaned_df.tail()


def get_symbols_pair():
    symbols_df = get_symbols()
    return symbols_df['symbol']


get_symbols_pair()


def get_base_currency():
    symbols_df = get_symbols()
    return symbols_df['baseCurrency']


get_base_currency()


def get_quote_currency():
    symbols_df = get_symbols()
    return symbols_df['quoteCurrency']


get_quote_currency()


def get_deposit_list(currency=None, page=None, pageSize=None):
    url = '/api/v1/deposits'
    headers = get_headers(url, 'GET')
    params = {}
    if currency:
        params['currency'] = currency
    if page:
        params['page'] = page
    if pageSize:
        params['pageSize'] = pageSize
    
    response = requests.get('https://api.kucoin.com' + url, headers=headers, params=params)
    if response.status_code == 200:
        deposit_list = response.json()
        return deposit_list
    else:
        print('Failed to get deposit list. Error code:', response.status_code)


get_deposit_list()


def get_base_fee():
    url = '/api/v1/base-fee'
    headers = get_headers(url, 'GET')
    response = requests.get('https://api.kucoin.com'+url, headers=headers)
    if response.status_code == 200:
        fees_data = response.json()['data']
        fees_df = pd.DataFrame(fees_data, index=[0])
        return fees_df
    else:
        print('Failed to get trade fees data. Error code:', response.status_code)


get_base_fee()


def get_actual_fee_rate(symbol):
    url = '/api/v1/trade-fees'
    headers = get_headers(url, 'GET')
    response = requests.get('https://api.kucoin.com'+url+'?symbols='+symbol, headers=headers)
    if response.status_code == 200:
        fees_data = response.json()['data']
        fees_df = pd.DataFrame(fees_data)
        return fees_df
    else:
        print('Failed to get actual fee rate data. Error code:', response.status_code)


get_actual_fee_rate('KNC-USDT')


def get_24hr_stats(symbol):
    url = 'https://api.kucoin.com/api/v1/market/stats'
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = json.loads(response.text)['data']
    return data


get_24hr_stats('KNC-USDT')


def get_market_list():
    endpoint = 'https://api.kucoin.com/api/v1/markets'
    response = requests.get(endpoint)
    data = json.loads(response.content)
    markets = data['data']
    print(markets)


get_market_list()


def get_trade_histories(symbol):
    url = 'https://api.kucoin.com/api/v1/market/histories?symbol={}'.format(symbol)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


#get_trade_histories('KNC-BTC')


def get_currencies():
    url = '/api/v1/currencies'
    response = requests.get('https://api.kucoin.com' + url)
    if response.status_code == 200:
        currencies_data = response.json()
        return currencies_data
    else:
        print('Failed to get currencies data. Error code:', response.status_code)


#get_currencies()


def get_fiat_price(symbol):
    url = 'https://api.kucoin.com/api/v1/prices'
    params = {"symbols": symbol}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()['data']
        return float(data[symbol])
    else:
        print(f"Failed to get {symbol} price. Error code:", response.status_code)


get_fiat_price('USDT')


def get_klines(symbol, interval='1day'):
    url = f'https://api.kucoin.com/api/v1/market/candles?type={interval}&symbol={symbol}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['data']
        klines_data = pd.DataFrame(data, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
        klines_data['time'] = pd.to_datetime(klines_data['time'], unit='ms')
        klines_data.set_index('time', inplace=True)
        klines_data = klines_data.astype(float)
        return klines_data
    else:
        print(f'Failed to get {symbol} Klines data. Error code:', response.status_code)
        return None


symbol = 'BTC-USDT'
interval = '1day'
klines_data = get_klines(symbol, interval)
klines_data.head()


def get_investment_data(url='/api/v1/accounts'):
    headers = get_headers(url, 'GET')
    response = requests.get(f'https://api.kucoin.com{url}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data['data'])
    else:
        print(f"Failed to get investment data. Error code: {response.status_code}")
        return None


get_investment_data()


def get_assets_data():
    tickers = get_all_tickers()['data']['ticker']
    balances = get_account_balance()
    assets_data = {}
    for row in balances:
        currency = row['currency']
        holdings = row['balance']
        ticker = next((item for item in tickers if item['symbol'] == f"{currency}-USDT"), None)
        if ticker is not None:
            price = float(ticker['last'])
            value = price * float(holdings)
            asset_data = {'symbol': currency, 'holdings': holdings, 'price': price, 'value': value}
            assets_data[currency] = asset_data
    return assets_data


get_assets_data()


def get_ohlc_data(symbol, interval='1day', columns=['timestamp', 'open', 'close', 'high', 'low', 'volume', 'turnover']):
    url = f'https://api.kucoin.com/api/v1/market/candles?symbol={symbol}&type={interval}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()['data']
        ohlc_data = []
        for candle in data:
            ohlc_data.append({
                columns[0]: candle[0],
                columns[1]: float(candle[1]),
                columns[2]: float(candle[4]),
                columns[3]: float(candle[2]),
                columns[4]: float(candle[3]),
                columns[5]: float(candle[5]),
                columns[6]: float(candle[6])
            })
        return ohlc_data
    else:
        print(f'Failed to get {symbol} OHLC data. Error code:', response.status_code)


#get_ohlc_data('KNC-USDT', '1day')


def get_total_portfolio_value():
    tickers = get_all_tickers()['data']['ticker']
    balances = get_account_balance()
    total_value = 0.0
    for row in balances:
        currency = row['currency']
        holdings = row['balance']
        ticker = next((item for item in tickers if item['symbol'] == f"{currency}-USDT"), None)
        if ticker is not None:
            price = float(ticker['last'])
            value = price * float(holdings)
            total_value += value
    return total_value


get_total_portfolio_value()


def get_total_profit_loss():
    balances = get_account_balance()
    total_profit_loss = 0.0
    for balance in balances:
        currency = balance['currency']
        holdings = float(balance['balance'])
        if holdings == 0:
            continue
        ticker = next((item for item in get_all_tickers()['data']['ticker'] if item['symbol'] == f"{currency}-USDT"), None)
        if ticker:
            price = float(ticker.get('last', 0))
            avg_price = float(balance.get('avgPrice', 0))
            profit_loss = (price - avg_price) * holdings
            total_profit_loss += profit_loss
    return total_profit_loss


get_total_profit_loss()



