import yfinance as yf
import pandas as pd
import numpy as np
import hvplot.pandas
import matplotlib.pyplot as plt
import holoviews as hv

def calculate_statistics(symbols, start_date, end_date):
    if not isinstance(symbols, list):
        symbols = [symbols]
    dfs = []
    for symbol in symbols:
        data = yf.download(symbol, start=start_date, end=end_date)
        close = data[['Close']].rename(columns={'Close': symbol})
        dfs.append(close)

    # merge data for all symbols
    ticker_data = pd.concat(dfs, axis=1)

    all_data = []
    for symbol in symbols:
        symbol_data = ticker_data[symbol]
        symbol_daily_returns = symbol_data.pct_change()
        symbol_cumulative_returns = (1 + symbol_daily_returns).cumprod() - 1
        data = pd.DataFrame({   
            "Symbol": symbol,
            "Close Price": symbol_data,
            "Daily Returns": symbol_daily_returns,
            "Cumulative Returns": symbol_cumulative_returns
        })
        all_data.append(data)      
    all_data_df = pd.concat(all_data, axis=0)
    return all_data_df

# Plot daily returns & cumulative returns for all symbols
def plot_daily_returns(all_data_df):
    daily_returns_plot = all_data_df.hvplot.line(
        x='Date', 
        y='Daily Returns', 
        ylabel='Daily Returns', 
        xlabel='Date', 
        groupby='Symbol',
        title='Daily Returns by Symbol'
    )
    return daily_returns_plot

def plot_cumulative_returns(all_data_df):
    cumulative_returns_plot = all_data_df.hvplot.line(
        x='Date', 
        y='Cumulative Returns', 
        xlabel='Date', 
        ylabel='Cumulative Returns', 
        groupby='Symbol', 
        title='Cumulative Returns by Symbols',
        legend='bottom_left'
    )    
    return cumulative_returns_plot


def calculate_stock_betas(symbols, start_date, end_date, index='^GSPC'):
    all_data_df = calculate_statistics(symbols, start_date, end_date)
    
    ticker_returns = all_data_df.drop(columns=["Close Price","Cumulative Returns"])
    ticker_returns = ticker_returns.pivot_table(values='Daily Returns', index='Date', columns='Symbol')
    
    index_data = yf.download(index, start=start_date, end=end_date, group_by='ticker')
    index_data = index_data.drop(columns=["Open","High","Low","Adj Close","Volume"])
    index_data.columns = ['_'.join(col).strip() for col in index_data.columns.values]
    index_data.columns = [col.split("_")[0] for col in index_data.columns]
    index_data = index_data.rename(columns={index_data.columns[-1]: "Index"})
    index_returns = index_data.pct_change()
    index_returns_df = pd.DataFrame(index_returns)
    index_returns = index_returns_df.pivot_table(index='Date', values='Index')
    
    combined_returns=pd.concat([ticker_returns,index_returns],axis='columns',join='inner')
    
    beta_dict = {}
    for symbol in symbols:
        cov = combined_returns[symbol].cov(combined_returns.iloc[:,-1])
        var = combined_returns.iloc[:,-1].var()
        beta = round(cov / var, 2)
        beta_dict[symbol] = beta

    beta_df = pd.DataFrame.from_dict(beta_dict, orient='index', columns=['Beta'])
    
    beta_plot = beta_df.hvplot.bar(
        x='index', 
        y='Beta', 
        xlabel='Symbol', 
        ylabel='Beta', 
        title='Stock Betas',
        color='orange',
        hover_color = 'green'
    )
    return beta_df

def calculate_sharpe_ratios(symbols, start_date, end_date, index='^GSPC'):
    all_data_df = calculate_statistics(symbols, start_date, end_date)
    
    ticker_returns = all_data_df.drop(columns=["Close Price","Cumulative Returns"])
    ticker_returns = ticker_returns.pivot_table(values='Daily Returns', index='Date', columns='Symbol')
    
    index_data = yf.download(index, start=start_date, end=end_date, group_by='ticker')
    index_data = index_data.drop(columns=["Open","High","Low","Adj Close","Volume"])
    index_data.columns = ['_'.join(col).strip() for col in index_data.columns.values]
    index_data.columns = [col.split("_")[0] for col in index_data.columns]
    index_data = index_data.rename(columns={index_data.columns[-1]: "Index"})
    index_returns = index_data.pct_change()
    index_returns_df = pd.DataFrame(index_returns)
    index_returns = index_returns_df.pivot_table(index='Date', values='Index')
    
    combined_returns=pd.concat([ticker_returns,index_returns],axis='columns',join='inner')
    
    sharpe_ratio_dict = {}
    for symbol in symbols:
        sharpe_ratios_symbol = round((combined_returns[symbol].mean()) *100/ (combined_returns[symbol].std() * np.sqrt(252)),4)
        sharpe_ratios_index = round((combined_returns.iloc[:, -1].mean())*100 / (combined_returns.iloc[:, -1].std() * np.sqrt(252)),4)
        sharpe_ratio_dict[symbol] = sharpe_ratios_symbol
        sharpe_ratio_dict["Index"] = sharpe_ratios_index
        
    sharpe_ratio_df = pd.DataFrame.from_dict(sharpe_ratio_dict, orient='index', columns=['Sharpe Ratio'])
    
    sharpe_ratio_plot = sharpe_ratio_df.hvplot.bar(
        x='index', 
        y='Sharpe Ratio', 
        xlabel='Symbol', 
        ylabel='Sharpe Ratio', 
        title='Sharpe Ratios',
        color='orange',
        hover_color = 'green'
    ).opts(yformatter='%.2f%%')
    
    return sharpe_ratio_df