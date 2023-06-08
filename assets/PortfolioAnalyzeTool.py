import yfinance as yf
import pandas as pd
import numpy as np
import hvplot.pandas
import matplotlib.pyplot as plt
import holoviews as hv

def portfolio_analysis(symbols, weights, index, start_date, end_date):
    # Use yahoo finance data to test the code
    ticker_data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker')

    if len(symbols) == 1:
        columns = []
        for column in ticker_data.columns.values:
            columns.append((symbols[0], column))
        ticker_data.columns = pd.MultiIndex.from_tuples(columns)

    ticker_data = ticker_data.drop(columns=["Open","High","Low","Adj Close","Volume"], level=1)
    ticker_data.columns = ['_'.join(col).strip() for col in ticker_data.columns.values]
    ticker_data.columns = [col.split("_")[0] for col in ticker_data.columns]
    
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
    all_data_df.groupby('Symbol')

    ticker_returns = all_data_df.drop(columns=["Close Price","Cumulative Returns"])
    ticker_returns = all_data_df.pivot_table(values='Daily Returns', index='Date', columns='Symbol')

    portfolio_returns = ticker_returns.dot(weights)
    portfolio_returns = pd.DataFrame(portfolio_returns, columns=["Portfolio Returns"])

    index_data = yf.download(index, start=start_date, end=end_date, group_by='ticker')
    index_data = index_data.drop(columns=["Open","High","Low","Adj Close","Volume"])
    index_data.columns = ['_'.join(col).strip() for col in index_data.columns.values]
    index_data.columns = [col.split("_")[0] for col in index_data.columns]
    index_data = index_data.rename(columns={index_data.columns[-1]: "Index"})

    index_returns = index_data.pct_change()
    cumulative_returns_index = (1 + index_returns).cumprod() - 1 
    index_returns_df = pd.DataFrame(cumulative_returns_index)
    index_returns_df = index_returns_df.pivot_table(index='Date', values='Index')

    cumulative_returns_portfolio = (1 + portfolio_returns).cumprod() - 1 
    
    cumulative_returns_portfolio_plot = cumulative_returns_portfolio.hvplot.line(
        x='Date', 
        y='Portfolio Returns',
        ylabel='Portfolio Returns', 
        xlabel='Date', 
        title='Portfolio Cumulative Returns'
    ) * index_returns_df.hvplot.line(
        x='Date', 
        y='Index', 
        ylabel='Index Returns', 
        xlabel='Date', 
        title='Index Cumulative Returns'
    )
    
    
    combined_returns=pd.concat([portfolio_returns,index_returns],axis='columns',join='inner')
    cov = combined_returns["Portfolio Returns"].cov(combined_returns["Index"])
    var = combined_returns["Index"].var()
    portfolio_beta = round(cov / var,2)

    # Calculate Sharpe Ratio
    sharpe_ratios_portfolio = round((combined_returns["Portfolio Returns"].mean())*100 / (combined_returns["Portfolio Returns"].std() * np.sqrt(252)), 4)
    sharpe_ratios_index = round((combined_returns["Index"].mean()) *100/ (combined_returns["Index"].std() * np.sqrt(252)), 4)

    # create a DataFrame with sharpe ratios
    sharpe_ratios = pd.DataFrame({
        "Sharpe Ratio": [sharpe_ratios_index, sharpe_ratios_portfolio],
        "Asset": ["Index", "Portfolio"]
    })

    # plot the DataFrame as a bar chart
    sharpe_ratios_plot = sharpe_ratios.hvplot.bar(
        x="Asset", 
        y="Sharpe Ratio", 
        xlabel="Asset", 
        ylabel="Sharpe Ratio", 
        title="Sharpe Ratios",
        color = "orange",
        hover_color = "green"
    )
    return portfolio_beta, sharpe_ratios, cumulative_returns_portfolio, index_returns_df