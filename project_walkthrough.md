# Project walkthrough
Details for application usage.

## Getting started
![Home screen](miscellaneous/id_home_screen.png)  
Users begin by navigating to the following web address:  
[https://fintech1.richedev.com](https://fintech1.richedev.com)  
The home page of the application provides users a login link in the top-right corner. Users are required to log in.

## Logging in
![Login screen](miscellaneous/id_login_screen.png)  
The application utilizes a social login service provided by [Auth0](https://auth0.com/). Users are requested to log in using one of the social methods provided.

## Current investments
![Current investments screen](miscellaneous/id_current_investments_screen.png)  
Upon logging-in, users are brought to the *Current investments* screen where, if applicable, their current investments are displayed. A tabbed view allows users to view their current investments across multiple exchanges.

## Historical investments
![Historical investments screen](miscellaneous/id_historical_investments_screen.png)  
The *Historical investments* screen displays users' historical investment data, if applicable. A tabbed view allows users to view their historical investments across multiple exchanges.

## Portfolio planner
![Portfolio planner screen](miscellaneous/id_portfolio_planner_screen.png)
The *Portfolio planner* screen provides users with a tool to draft and analyze new portfolios. Drafted portfolios must contain a name, an investment period, at least one ticker, and a total ticker weight equaling 1 across all tickers before it can be saved to the application's database.
  
![Portfolio drafted view](miscellaneous/id_portfolio_drafted_view.png)  
![Portfolio calculations view 01](miscellaneous/id_portfolio_calculations_view_01.png)  
![Portfolio calculations view 02](miscellaneous/id_portfolio_calculations_view_02.png)  
![Portfolio calculations view 03](miscellaneous/id_portfolio_calculations_view_03.png)  
Upon drafting a portfolio, users can run calculations to analyze historical portfolio performance and related statistics, including:
- Sharpe ratio
- Beta
- Daily returns
- Cumulative returns
- Daily closing price
  
![Portfolio simulations view 01](miscellaneous/id_portfolio_simulations_view_01.png)  
![Portfolio simulations view 02](miscellaneous/id_portfolio_simulations_view_02.png)  
![Portfolio simulations view 03](miscellaneous/id_portfolio_simulations_view_03.png)  
By including an investment amount with a drafted portfolio, users can also run simulations to analyze theoretical future performance of the portfolio with statistics such as:
- Mean
- Standard deviation
- Quartiles
- 95% CI lower
- 95% CI upper
- Cumulative return trajectories
- Distribution of final cumulative returns

## Account management
![Account management screen](miscellaneous/id_account_management_screen.png)  
The *Account management* screen allows users to view their connected exchanges, along with information relating to the exchanges.

## Logging out
![Logout view](miscellaneous/id_logout_view.png)  
For the privacy of personal information, users are encouraged to log out when not using the application.