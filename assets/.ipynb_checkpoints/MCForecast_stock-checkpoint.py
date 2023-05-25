import pandas as pd
import yfinance as yf
from MCForecastTools import MCSimulation

def run_monte_carlo_simulation(symbol: str, start_date: str, end_date: str, num_sims: int, *, num_years: int) -> dict:
    # Download historical data
    ticker_data = yf.download(symbol, start=start_date, end=end_date)
    ticker_data = pd.concat([ticker_data], axis=1, keys=[symbol])
    ticker_data = ticker_data.rename(columns={"Close":"close"})

    # Run Monte Carlo simulation
    num_trading_days = 252 * num_years
    
    MC_ticker = MCSimulation(
        portfolio_data = ticker_data,
        num_simulation = num_sims,
        num_trading_days = num_trading_days
    )
    MC_ticker.calc_cumulative_return()

    # Compute summary statistics from the simulated daily returns
    simulated_returns_data = {
        "mean": list(MC_ticker.simulated_return.mean(axis=1)),
        "median": list(MC_ticker.simulated_return.median(axis=1)),
        "min": list(MC_ticker.simulated_return.min(axis=1)),
        "max": list(MC_ticker.simulated_return.max(axis=1)),
        "std": list(MC_ticker.simulated_return.std(axis=1))
    }
    df_simulated_returns = pd.DataFrame(simulated_returns_data)

    # Compute and print summary statistics
    tbl = MC_ticker.summarize_cumulative_return()
   

    # Compute 95% confidence interval
    ci_lower = round(tbl[8]*10000,2)
    ci_upper = round(tbl[9]*10000,2)

    # Return summary statistics and confidence interval
    return {"summary_statistics": tbl, "confidence_interval": (ci_lower, ci_upper)}