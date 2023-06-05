# Investor's Dream
Dash web-application for managing personal investments, as well as planning and simulating theoretical portfolios.

## Project details
### Description and purpose
<p align="justify">The Investor's Dream application is a real-time portfolio tool that allows users to track historic and current investments while also planning potential future investments. Historic and current investments are downloaded from an exchange's server via the exchange's API and displayed in the application. Users can draft and analyze theoretcial portfolios utilizing a variety of graphical and tabular methods. Drafted portfolios can be saved to the application's PostgreSQL database. Simulations can be performed on theoretical portfolios and analyzed in tabular and/or graphical formats.</p>
    
### Questions
1. How can an investor compare multiple simulated portfolios to determine their ideal investment portfolio?
2. How can an investor make the most money with the least amount of risk?
3. Which asset mix can provide the strongest portfolio given current market conditions?
4. In what ways can an investor visualize their investment planning data?
5. Who could use this application?
6. How can we diversify an investor’s portfolio such that it can be profitable and have stocks with a security worth investing in?
7. How do we present information to an investor looking to diversify their stock portfolio and maximize their profits such that they can study the information and make an informed decision before investing?

### Answers
#### Portfolio drafting and analysis
<p align="justify">The Investor's Dream application allows users to draft portfolios of their choosing and run calculations on historical data to determing portfolio risk. Calculations include:</p>  
  
- Sharpe ratio  
- Beta  
- Daily returns  
- Cumulative returns  
- Daily closing price  
    
<p align="justify">The application employs validation techniques to ensure accurate portfolio drafting and analysis. Drafted portfolios can be saved to the application's database for future reference and comparison.</p>

#### Monte Carlo Simulation and analysis
<p align="justify">To analyze the results of a Monte Carlo simulation, financial analysts often use metrics such as Sharpe ratios, standard deviations, and correlations. The Sharpe ratio, for example, measures the excess return of a portfolio relative to the risk-free rate, divided by its standard deviation. The standard deviation measures the degree of variability of the portfolio's returns, while correlations measure the degree to which the returns of different assets move together. In finance, Monte Carlo simulations are often used to analyze the risk and return of a portfolio of assets. The technique involves creating a model of the portfolio that takes into account the historical performance of the assets, as well as their expected future returns, volatility, and correlations with one another.</p>

#### Further information
For further information, please refer to our [PowerPoint presentation](miscellaneous/Investor's%20Dream%20Project%201.pptx).

### Running the application
Open your browser and go to the following url:  
https://fintech1.richedev.com/

### Application walkthrough
Please refer to our [project walkthrough](project_walkthrough.md) for detailed instructions on how to use the application.

### Data conclusions
<p align="justify">The Investor's Dream application provides investors with the tools they require to monitor existing investments and, perhaps more importantly, make informed decisions regarding future investments.</p>

## Resources and technology employed
![Tools used](miscellaneous/tools_used.png)  
- Python
  - APIs
    - Alpaca
    - Auth0
    - KuCoin
  - Dash
  - Flask
  - Holoviews
  - Monte Carlo simulator
  - Numpy
  - Pandas
  - Plotly
  - SQLAlchemy
  - YFinance
- SQL
  - PostgreSQL
- CSS
- HTML

## Developers
- [Andrea Delgadillo Tomasevich](https://github.com/visionaryspirit)
- [Dmitry Chalganov](https://github.com/Imbadimasa)
- [John Yin](https://github.com/Ziqiangyin)
- [Julian Ritchey](https://github.com/julianritchey)
    
#### Dreaming doesn't cost anything
*Humble beginnings, abundant future*


