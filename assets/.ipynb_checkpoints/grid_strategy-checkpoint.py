import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pandas as pd

def grid_trading_strategy(symbol, test_start_date, test_end_date, initial_cash= 200000, initial_quantity= 1000, quantity=100, percentage_change= 0.03, max_grid_count=20):
    # Download stock data
    stock_data = yf.download(symbol, start=test_start_date,end=test_end_date)
    stock_data.index = pd.to_datetime(stock_data.index, unit='1d')
    # Plotting
    # plt.figure(figsize=(20, 10))
    # plt.plot(stock_data['Close'], label='Stock Price')
    # plt.tight_layout()
    # plt.show()

    # Create test_df for backtesting
    test_df = stock_data.loc[(stock_data.index >= test_start_date) & (stock_data.index <= test_end_date), 'Close'].copy()
    test_df = test_df.reset_index()
    test_df.columns = ['Date', 'Close']
    test_df = test_df.set_index('Date')

    # Calculate grid levels
    grid_levels = []
    grid_price = test_df.iloc[0]['Close']
    nearest_index = test_df.index.get_indexer([test_start_date], method='nearest')[0]
    price_up = test_df.iloc[nearest_index]['Close']
    price_down = test_df.iloc[nearest_index]['Close']

    while len(grid_levels) < max_grid_count:
        grid_levels.append(round(price_up, 2))
        price_up += round((grid_price * percentage_change), 2)

    while len(grid_levels) < (2 * max_grid_count - 1):
        grid_levels.append(round(price_down, 2))
        price_down -= round((grid_price * percentage_change), 2)

    grid_levels = sorted(grid_levels)
    
    # Initialize variables
    cash = initial_cash
    stock_qty = 0
    stock_value = 0.0

    # Create a new DataFrame for trade records
    trade_records = pd.DataFrame(columns=['Date', 'Action', 'Quantity', 'Price'])

    # Buy initial shares on the start date at the start price
    start_price = test_df.iloc[0]['Close']
    if cash >= start_price * initial_quantity:
        stock_qty = initial_quantity
        stock_value += start_price * initial_quantity
        cash -= start_price * initial_quantity
        trade_records = pd.concat([trade_records, pd.DataFrame({'Date': [test_df.index[0]], 'Action': ['Buy'], 'Quantity': [initial_quantity], 'Price': [start_price], 'StockQty': [stock_qty], 'StockValue': [stock_value], 'Cash': [cash]})], ignore_index=True)
    # Backtesting
    for i in range(1, len(test_df)):
        Date = test_df.index[i]
        trade_price = test_df.iloc[i]['Close']
        previous_price = test_df.iloc[i-1]['Close']

        # Check if trigger the buy condition
        if trade_price < previous_price:
            for j in range(1, len(grid_levels) - 1):
                grid_price = grid_levels[j]
                prev_grid_price = grid_levels[j-1]
                if trade_price <= grid_price and trade_price >= prev_grid_price and cash >= trade_price * quantity:
                    stock_qty += quantity
                    stock_value = trade_price * stock_qty
                    cash -= trade_price * quantity
                    trade_records = pd.concat([trade_records, pd.DataFrame({'Date': [Date], 'Action': ['Buy'], 'Quantity': [quantity], 'Price': [trade_price], 'StockQty': [stock_qty], 'StockValue': [stock_value], 'Cash': [cash]})], ignore_index=True)
                    break

        # Check if trigger the sell condition
        elif trade_price > previous_price:
            for j in range(len(grid_levels) - 2, 0, -1):
                grid_price = grid_levels[j]
                next_grid_price = grid_levels[j+1]
                if trade_price >= grid_price - 1 and trade_price <= next_grid_price + 1 and stock_qty >= quantity:
                    stock_qty -= quantity
                    stock_value = trade_price * stock_qty
                    cash += trade_price * quantity
                    trade_records = pd.concat([trade_records, pd.DataFrame({'Date': [Date], 'Action': ['Sell'], 'Quantity': [quantity], 'Price': [trade_price], 'StockQty': [stock_qty], 'StockValue': [stock_value], 'Cash': [cash]})], ignore_index=True)
                    break

    # Plotting
#     plt.figure(figsize=(20, 10))
#     plt.plot(test_df['Close'], label='Stock Price')

#     for level in grid_levels:
#         plt.axhline(y=level, color='r', linestyle='--')

#     for i in range(len(trade_records)):
#         record = trade_records.iloc[i]
#         if record['Action'] == 'Buy':
#             plt.scatter(record['Date'], record['Price'], color='g', marker='^',s=100)
#         elif record['Action'] == 'Sell':
#             plt.scatter(record['Date'], record['Price'], color='r', marker='v',s=100)

#     plt.title('Grid Trades Records', fontsize=20)
#     plt.xlabel('Date', fontsize=12)
#     plt.ylabel('Price', fontsize=12)

#     plt.gca().xaxis.set_major_locator(mdates.DayLocator())
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

#     plt.xticks(rotation=80, fontsize=8)
#     plt.yticks(fontsize=10)
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
    
    # Calculate backtest result
    test_start_date = pd.to_datetime(test_start_date).date()
    test_end_date = pd.to_datetime(test_end_date).date()

    portfolio_value = round(cash + stock_value, 2)
    pnl = round(portfolio_value - initial_cash, 2)
    absolute_return = round(pnl / initial_cash * 100, 2)
    # backtest_days = (test_end_date - test_start_date).days + 1
    # annual_return = round((1 + absolute_return) ** (365 / backtest_days) - 1, 2)

    print("Backtest Result:")
    print(f"Initial Cash: {initial_cash}")
    print(f"Final Value: {portfolio_value}")
    print(f"Profits: {pnl}")
    print(f"Return Rate: {absolute_return}%")
    # print(f"Annualized Return: {annual_return}%")
    # print(f"Backtest days: {backtest_days}")
    
    portfolio_data = [
        {'Metric': 'Initial cash', 'Value': f"USD {initial_cash:,.2f}"},
        {'Metric': 'Final value', 'Value': f"USD {portfolio_value:,.2f}"},
        {'Metric': 'Profit/loss', 'Value': f"USD {pnl:,.2f}"},
        {'Metric': 'Return rate', 'Value': f"{absolute_return}%"}
    ]
    
    return stock_data, test_df, grid_levels, trade_records, portfolio_data


