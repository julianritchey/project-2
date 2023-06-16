import pandas as pd
import yfinance as yf
import numpy as np
import hvplot.pandas
from finta import TA
import talib as ta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore") 

def generate_and_plot_ema_signals(symbol, start_date, end_date):
    # Get stock data
    data = yf.download(symbol, start=start_date, end=end_date)
    data.index = pd.to_datetime(data.index, unit='1d')

    # Create a DataFrame with the index and Close column from the dataset
    ema_signals_df = data.loc[:, ["Close"]].copy()
    trix_window = 15
    signal_length = 9
        
    # Calculate the ADX indicator
    adx_df = data.loc[:, ["High", "Low", "Close"]].copy()
    adx_df["avg"] = ta.ADX(adx_df["High"], adx_df["Low"], adx_df["Close"], timeperiod=20)

    # Generate the single, double and triple exponential moving averages (15 days, respectively)
    ema_signals_df["SingleEMA"] = data["Close"].ewm(span=trix_window).mean()
    ema_signals_df["DoulbeEMA"] = ema_signals_df["SingleEMA"].ewm(span=trix_window).mean()
    ema_signals_df["TripleEMA"] = ema_signals_df["DoulbeEMA"].ewm(span=trix_window).mean()
    ema_signals_df["TRIX"] = (ema_signals_df["TripleEMA"]-ema_signals_df["TripleEMA"].shift(1))/ema_signals_df["TripleEMA"].shift(1)*10000
    ema_signals_df["Signal"] = ema_signals_df["TRIX"].ewm(span=signal_length).mean()
    ema_signals_df["ADX"]=adx_df["avg"]

    # Generate the trading signal 1 or 0
    ema_signals_df["Delta"] = 0.0
    ema_signals_df["Delta"][trix_window:] = np.where(
        (ema_signals_df["TRIX"][trix_window:] > ema_signals_df["Signal"][trix_window:]),
        1.0, 0.0)
    
    # Set Entry/Exit column based on condition
    # ema_signals_df["ADX_condition"] = (ema_signals_df["ADX"][trix_window:] >= 25).astype(int)

    # Calculate the points in time at which a position should be taken, 1 or -1
    ema_signals_df["Entry/Exit"] = 0.0
    ema_signals_df["Entry/Exit"] = ema_signals_df["Delta"].diff()
    # ema_signals_df.loc[ema_signals_df["ADX_condition"] == 1, "Entry/Exit"] = ema_signals_df["Delta"].diff()
    
    # Plot entry and exit signals
    exit = ema_signals_df[ema_signals_df["Entry/Exit"] == -1.0]["Close"]
    entry = ema_signals_df[ema_signals_df["Entry/Exit"] == 1.0]["Close"]
    moving_avgs = ema_signals_df[["TRIX", "Signal"]]
    
#     plt.figure(figsize=(10, 6))
#     plt.plot(ema_signals_df["Close"], label="Close")
#     plt.plot(moving_avgs, linewidth=1.5, label=["TRIX", "Signal"])
#     plt.scatter(exit.index, exit, color="red", marker="v", s=40, label="Exit")
#     plt.scatter(entry.index, entry, color="purple", marker="^", s=40, label="Entry")
#     plt.xlabel("Index")
#     plt.ylabel("Price in $")
#     plt.title("Exit Positions Relative to Close Price")
#     plt.legend(labels=["Close", "TRIX", "Signal", "Exit", "Entry"])
#     plt.tight_layout()
#     plt.show()
    
#     plt.figure(figsize=(10, 3))
#     plt.plot(ema_signals_df["ADX"], label="ADX")
#     plt.title("Average Directional Index")
#     plt.tight_layout()
#     plt.show()    
    
    return(ema_signals_df)

#Backtest the trades
def evaluate_trades(ema_signals_df, symbol):

    # Set initial capital
    initial_capital = float(100000)
    # Set the share size
    share_size = round(initial_capital / ema_signals_df["Close"].max())
    
    ema_signals_df['Position'] = share_size * ema_signals_df['Delta']
    ema_signals_df['Entry/Exit Position'] = ema_signals_df['Position'].diff()
    ema_signals_df['Portfolio Holdings'] = ema_signals_df['Close'] * ema_signals_df['Position']
    ema_signals_df['Portfolio Cash'] = initial_capital - (ema_signals_df['Close'] * ema_signals_df['Entry/Exit Position']).cumsum()
    ema_signals_df['Portfolio Total'] = ema_signals_df['Portfolio Cash'] + ema_signals_df['Portfolio Holdings']
    ema_signals_df['Portfolio Daily Returns'] = ema_signals_df['Portfolio Total'].pct_change()
    ema_signals_df['Portfolio Cumulative Returns'] = (1 + ema_signals_df['Portfolio Daily Returns']).cumprod() - 1
    
    
    # plt.figure(figsize=(10,6))
    # plt.plot(ema_signals_df["Portfolio Cumulative Returns"], label="Portfolio Cumulative Returns")
    # plt.xlabel("Index")
    # plt.ylabel("Return in %")
    # plt.title("Portfolio Cumulative Returns by MACD Strategy")
    # plt.legend()
    # plt.tight_layout()
    # plt.show()

    trade_evaluation_df = pd.DataFrame(
        columns=[
            "Stock",
            "Entry Date",
            "Exit Date",
            "Shares",
            "Entry Share Price",
            "Exit Share Price",
            "Entry Portfolio Holding",
            "Exit Portfolio Holding",
            "Profit/Loss"]
    )
    for index, row in ema_signals_df.iterrows():
        if row["Entry/Exit"] == 1:
            entry_date = index
            entry_portfolio_holding = row["Portfolio Holdings"]
            share_size = row["Entry/Exit Position"]
            # share_size = round(initial_capital / row["Close"])
            entry_share_price = row["Close"]

        elif row["Entry/Exit"] == -1:
            exit_date = index
            exit_portfolio_holding = abs(row["Close"] * row["Entry/Exit Position"])
            exit_share_price = row["Close"]
            profit_loss = exit_portfolio_holding - entry_portfolio_holding
            trade_evaluation_df = trade_evaluation_df.append(
                {
                    "Stock": symbol,
                    "Entry Date": entry_date,
                    "Exit Date": exit_date,
                    "Shares": share_size,
                    "Entry Share Price": entry_share_price,
                    "Exit Share Price": exit_share_price,
                    "Entry Portfolio Holding": entry_portfolio_holding,
                    "Exit Portfolio Holding": exit_portfolio_holding,
                    "Profit/Loss": profit_loss
                },
                ignore_index=True
            )

    return trade_evaluation_df

def evaluate_portfolio(ema_signals_df, trade_evaluation_df):
    # Create a list for the column name
    columns = ["Backtest"]

    # Create a list holding the names of the new evaluation metrics
    metrics = [
        "Annualized Return",
        "Cumulative Returns",
        "Annual Volatility",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Success Ratio",
        "Avg Profit per trade",
        "Avg Loss per trade"
    ]

    # Initialize the DataFrame with index set to the evaluation metrics and the column
    portfolio_evaluation_df = pd.DataFrame(index=metrics, columns=columns)

    portfolio_evaluation_df.loc["Annualized Return"] = (
        ema_signals_df["Portfolio Daily Returns"].mean() * 252
    )

    portfolio_evaluation_df.loc["Cumulative Returns"] = (
        ema_signals_df["Portfolio Cumulative Returns"][-1]
    )

    portfolio_evaluation_df.loc["Annual Volatility"] = (
        ema_signals_df["Portfolio Daily Returns"].std() * np.sqrt(252)
    )

    portfolio_evaluation_df.loc["Sharpe Ratio"] = (
        ema_signals_df["Portfolio Daily Returns"].mean() * 252
    ) / (
        ema_signals_df["Portfolio Daily Returns"].std() * np.sqrt(252)
    )

    portfolio_evaluation_df.loc["Success Ratio"] = len(trade_evaluation_df[trade_evaluation_df["Profit/Loss"] > 0]) / len(trade_evaluation_df)

    portfolio_evaluation_df.loc["Avg Profit per trade"] = trade_evaluation_df[trade_evaluation_df["Profit/Loss"] > 0]["Profit/Loss"].mean()

    portfolio_evaluation_df.loc["Avg Loss per trade"] = trade_evaluation_df[trade_evaluation_df["Profit/Loss"] < 0]["Profit/Loss"].mean()

    # Create a DataFrame that contains the Portfolio Daily Returns column
    sortino_ratio_df = ema_signals_df[["Portfolio Daily Returns"]].copy()

    # Create a column to hold downside return values
    sortino_ratio_df.loc[:, "Downside Returns"] = 0

    # Find Portfolio Daily Returns values less than 0,
    # square those values, and add them to the Downside Returns column
    sortino_ratio_df.loc[sortino_ratio_df["Portfolio Daily Returns"] < 0,
                         "Downside Returns"] = sortino_ratio_df["Portfolio Daily Returns"]**2

    # Calculate the annualized return value
    annualized_return = (
        sortino_ratio_df["Portfolio Daily Returns"].mean() * 252
    )

    downside_standard_deviation = (
        np.sqrt(sortino_ratio_df["Downside Returns"].mean()) * np.sqrt(252)
    )

    sortino_ratio = annualized_return / downside_standard_deviation

    # Add the Sortino ratio to the evaluation DataFrame
    portfolio_evaluation_df.loc["Sortino Ratio"] = sortino_ratio

    return portfolio_evaluation_df


