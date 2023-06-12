import pandas as pd
import yfinance as yf
import numpy as np
import hvplot.pandas
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

def train_and_predict_stock(symbol, start_date, end_date):
    def get_stock_data(symbol, start_date, end_date):
        data = yf.download(symbol, start=start_date, end=end_date)
        data.index = pd.to_datetime(data.index, unit='1d')
        return data

    stock_data = get_stock_data(symbol, start_date, end_date)
    stock_data = stock_data.filter(["Close"])
    stock_data = stock_data.rename(columns={"Close":"GT"})

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_prices = scaler.fit_transform(stock_data.values)

    moving_win_size=60

    all_x, all_y =[],[]
    for i in range(len(scaled_prices)-moving_win_size):
        x = scaled_prices[i:i+moving_win_size]
        y = scaled_prices[i+moving_win_size]
        all_x.append(x)
        all_y.append(y)

    all_x, all_y = np.array(all_x),np.array(all_y)

    DS_SPLIT = 0.8

    train_ds_size = round(all_x.shape[0]*DS_SPLIT)
    train_x, train_y = all_x[:train_ds_size],all_y[:train_ds_size]
    test_x, test_y = all_x[train_ds_size:],all_y[train_ds_size:]

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(train_x.shape[1],1)))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.summary()

    model.compile(optimizer="adam",loss="mean_squared_error")

    callback = EarlyStopping(monitor="val_loss",patience=10, restore_best_weights=True)

    model.fit(train_x, train_y,
             validation_split=0.2,
             callbacks=[callback],
             epochs=1000)

    preds=model.predict(test_x)
    preds=scaler.inverse_transform(preds)

    train_df=stock_data[:train_ds_size+moving_win_size]
    test_df=stock_data[train_ds_size+moving_win_size:]
    test_df=test_df.assign(Predict=preds)

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.plot(train_df["GT"],linewidth=2)
    plt.plot(test_df["GT"],linewidth=2)
    plt.plot(test_df["Predict"],linewidth=1)
    plt.xticks(rotation=45)
    plt.legend(["Train","GT","Predict"])
    plt.show()

    plt.plot(train_df["GT"][-20:],linewidth=2)
    plt.plot(test_df["GT"][:30],linewidth=2)
    plt.plot(test_df["Predict"][:30],linewidth=1)
    plt.xticks(rotation=45)
    plt.legend(["Train","GT","Predict"])
    plt.show()

    plt.plot(test_df["GT"][-10:],linewidth=2)
    plt.plot(test_df["Predict"][-10:],linewidth=1)
    plt.xticks(rotation=45)
    plt.legend(["GT","Predict"])
    plt.show()

    test_df = test_df.assign(Shifted=test_df["GT"].shift(1))
    test_df.iat[0, -1] = train_df.iat[-1, -1]

    predict_rmse = mean_squared_error(test_df["GT"], test_df["Predict"], squared=False)
    predict_cvrmse = predict_rmse / test_df["GT"].mean() * 100
    print("Predict CVRMSE:", predict_cvrmse)
    print("-----------------------------------------------------------")

    shifted_rmse = mean_squared_error(test_df["GT"], test_df["Shifted"], squared=False)
    shifted_cvrmse = shifted_rmse / test_df["GT"].mean() * 100
    print("Shifted CVRMSE:", shifted_cvrmse)

