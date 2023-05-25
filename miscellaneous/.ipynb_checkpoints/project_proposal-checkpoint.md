# Project Proposal
Project 1 for Fintech bootcamp.

## Project title
Investor's Dream

## Team members
- Andrea Delgadillo Tomasevich
- Dmitry Chalganov
- John Yin
- Julian Ritchey

## Project description/outline
The investor's dream is an application that performs the following functions:
- Tracks historic and existing investments;
- allows the investor to forecast potential portfolio scenarios.
The Investor's Dream application is a tool that allows an investor to track historic and current investments while also planning potential future investments. Historic and current investments, once downloaded from an exchange's server via the exchange's API, will be saved to the application's database for future reference. The user will also be able to visualize their investment history using a variety of charts. Simulations performed on theoretical portfolios will also be saved to the application's database so the investor can keep track of portfolio ideas they have already investigated. Results of portfolio simulations will be presented in tabular and/or graphical formats for the investor's analysis.

## Questions to answer
1. How can an investor compare multiple simulated portfolios to determine their ideal investment portfolio?
2. How can an investor make the most money with the laest amount of risk?
3. Which asset mix can provide the strongest portfolio given current market conditions?
4. In what ways can an investor visualize their investment planning data?
5. Who could use this application?

## Datasets to be Used:
- Historic market data.
- User investment data (from exchanges).

## Rough Breakdown of Tasks:
1. Create a function that will pull the data from an API
2. Clean the pulled data
3. Save the data into an SQL database
4. Visualize the pulled data
5. Display where the exchanges are located using GeoViews *Optional
6. Test the application once all the programming is completed (Group Effort)

## Notes:
- Focus on the long position, not the short position
- Are there any stocks that we like individually? *For testing
- Inputs from the user: How do their historic and current investments look? What stocks do they want to add to a portfolio? How many years do they want to invest in? What portfolios do they want to compare?
- Outputs to the user: Displays historic and current investment data. Displays risk and return of theoretical portfolios that they choose. Portfolios that users choose will be stored in a database.
