
# Feature Proposal for Investor's dream or Investor's collective 

>My feature proposal have 2 parts:

* Investor's risk Assessment model (A model that assesses and categorizes investors based on their risk tolerance or risk profile)
* Interactive financial educational tools (available to all users according to their needs, risk profile, etc)

## What are they exactly?

### Investor's risk assessment model

* Investor's dream doesn't leave anyone behind. We understand that one size doesn’t fit all. Our investors are diverse, have different needs, and therefore different goals for their investments.

* The application will now incorporate a model that will help our users determine what type of investors they are (Specially those who are new, don't have much experience, and need support)

* The model will be trained with the most important demographics/features such as: income, age, networth,employment, etc. The model will output categorical values: low risk investor(1), moderate risk investor(2), high risk investor(3), as per the Risk Tolerance Scale we saw in class.

* That way, we can create trading algorithms that will satisfy the needs of our 3 types of investors(Here's hoping :P) 

## Who is it for?

* Our investors will benefit from this assessment, investing is more than just putting your hard earned money in a fund. The number one reason why many amateur investors fail, including seasoned investors that lose a lot of money is in many cases lack of education, lack of awareness or the big three:

-Know yourself
-Know your investments
-Know your advisors

* Financial sovereignty begins with personal sovereignty. All users are encouraged to take the lead in their own learning, when we are "categorized" (low risk investor, moderate risk investor, high risk investor) gives power and authority to the user. Because you know what we will say: "Investor's dream doesn't take any responsability from your losses, this is not financial advice" :P

  
### Interactive financial educational tools

* Now, that we know where our investors stand, and we discover what their vision or goals are for their invesment, one part is that we create the algo trading models based on their risk profile. The other part is access to resources, if Iam a low risk investor because my income is limited, Iam afraid to lose money, or I don't trust this invesment world anyway because eveything is a scam! (You know some people like this...), or I just don't know what a sharpe ratio is, or standard deviation...

* Maybe some resources such as investing goals, expenses and budget planning may help...what are capital gains? what is a stock? How do I even interpret the beautiful graphs/plots that these fintech professionals have implemented in the platform :P 

## How will it/they be implemented? 

* The investor's risk assessment model will be trained on the most important features which have the most weight in determining what type of investors they are. The original data set is a US dataset with a TrueToleranceforRisk nunerical value as the y target. The Canadian dataset has pretty much all the same features as the US dataset, except it doesn't have the y target. So, the Canadian data set will be trained on the US model. (Will try different ones, will choose the one with highest accuracy). I was thinking a neural network categorical classification as our target will be 3 classes. 

* Then, it's all about creating the trading algorithms based on the type of investor that the model will output. Found a crypto library with python and it works with 4 of the major exchanges (Binance, Kraken, Kucoin, Coinbase...) The dataframes are currently set up in OHLCV format. For our high risk investors I was thinking to create a diversied portfolio, some crypto assets, some commodities...to make it realistic.

* Obviously, backtest these strategies, the alpaca backtesting on cloud is all set up for it. But we have finta as well. 

* For the interactive financial educational resources/tools it can be its own little thing that we can show in the presentation (in case we run into problems connecting to the application). The interactive financial tool can stand alone as its own little app that I can deploy to our project, it's a python framework library ( It doesn't require html like dash or flask :P). I can feed it the data I will be using to train the investor's risk assessment model.
* But more resources can be incorporated as well, it allows it for different types as I have seen in some demos.

