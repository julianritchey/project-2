# Feature Proposal
Strategy Selector

## What is it?
The Strategy Selector will allow users to activate or deactivate auto-trading (bot) strategies as they please. The feature will encorporate the following:
- Ability to activate a strategy on any ticker of the user's choosing.
  - User may select which exchange to use
- Ability to backtest a strategy on any ticker of the user's choosing.
  - If possible, user may select which exchange to use
- Display strategy details.
  - Timeframe (`1h`, `1D`, `HTF`, `LTF`, etc.)
  - Indicators utilized, if applicable (`BB`, `EMA`, `MA`, etc.)
  - Methodology (buy upon retest of market structure break, sell upon swing failure pattern, etc.)
- Display details regarding backtests performed for each strategy.
  - Max performance
  - Min performance
  - Sharpe ratio
  - Standard deviation
- Display details regarding strategies backtested for each ticker.
  - Same details as strategy backtests
  - Recommended strategies

## Who is it for?
The Strategy Selector is for users interested in using trading bots for their investments. Users may be interested in short-, mid- or long-term trading and should have strategies available to them for any timeframe.

## Where will it be located?
The Strategy Selector should be placed in one of two locations within the application:
- Separate page for bot trading.
- Same page as manual trading.

## How will it be implemented?
The Strategy Selector will require the following server-side implementations:
- Application-wide database of strategies and backtest details.
- User-specific database of active strategies and associated exchange accounts.
- Application-wide API connections to various exchanges.

The Strategy Selector will require the following client-side implementations:
- Form-submission for activating a strategy with a ticker and exchange account.
- Charts and tables for strategy-backtesting analysis.
- SQL queries for saving information to database tables.