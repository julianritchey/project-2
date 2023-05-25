# Import libraries and dependencies
# import os
# from imports import MCSimulation
# from dotenv import load_dotenv

# Define the function
def run_monte_carlo_simulation(api_key: str, secret_key: str, start_date: str, end_date: str, tickers, weights, num_simulation: int,*, num_years: int, investment: float):
    # Import dependencies
    from imports import MCSimulation
    import pandas as pd
    import alpaca_trade_api as tradeapi

    # Set Alpaca API key and secret
    alpaca_api_key = api_key
    alpaca_secret_key = secret_key

    # Initialize the Alpaca API
    api = tradeapi.REST(
        alpaca_api_key,
        alpaca_secret_key,
        api_version = "v2"
    )

    # Set timeframe to "1Day"
    timeframe = "1Day"

    # Get historical price data for the given tickers and date range
    df_ticker = api.get_bars(
        tickers,
        timeframe,
        start=start_date,
        end=end_date
    ).df

    # Reorganize the DataFrame
    # Separate ticker data
    ticker_data = {}
    for ticker in tickers:
        ticker_data[ticker] = df_ticker[df_ticker['symbol'] == ticker].drop('symbol', axis=1)

    # Concatenate the ticker DataFrames
    df_ticker = pd.concat(ticker_data.values(), axis=1, keys=ticker_data.keys())

    # Configure a Monte Carlo simulation to forecast five years cumulative returns
    MC_portfolio = MCSimulation(
        portfolio_data = df_ticker,
        weights = weights,
        num_simulation = num_simulation,
        num_trading_days = 252 * num_years
    )

    # Run the Monte Carlo simulation to forecast five years cumulative returns
    cumulative_returns = MC_portfolio.calc_cumulative_return()

    # Plot simulation outcomes
    # line_plot = MC_portfolio.plot_simulation()

    # Save the plot for future usage
    # line_plot.get_figure().savefig("MC_portfolio_sim_plot.png", bbox_inches="tight")

    # Plot probability distribution and confidence intervals
    # dist_plot = MC_portfolio.plot_distribution()

    # Save the plot for future usage
    # dist_plot.get_figure().savefig('MC_portfolio_dist_plot.png',bbox_inches='tight')

    # Fetch summary statistics from the Monte Carlo simulation results
    tbl = MC_portfolio.summarize_cumulative_return()

    # Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $10,000 investments in the given stocks
    ci_lower = round(tbl[8] * investment, 2)
    ci_upper = round(tbl[9] * investment, 2)

    # Return summary statistics and confidence interval
    # return {"summary_statistics": tbl, "confidence_interval": (ci_lower, ci_upper)}
    return cumulative_returns, tbl, ci_lower, ci_upper