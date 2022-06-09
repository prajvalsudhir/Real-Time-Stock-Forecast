import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import tensorflow as tf
from tensorflow.keras.models import load_model
from datetime import date
from datetime import timedelta
import yfinance as yf
from pickle import dump,load
from sklearn.preprocessing import MinMaxScaler

def predict_future(temp_input, x_input, model):
    lst_output = []
    n_steps = 100
    i = 0
    while (i < 30):

        if (len(temp_input) > 100):
            # print(temp_input)
            x_input = np.array(temp_input[1:])
            # print("{} day input {}".format(i,x_input))
            x_input = x_input.reshape(1, -1)
            x_input = x_input.reshape((1, n_steps, 1))  ## reshape to 100 timesteps
            # print(x_input)
            yhat = model.predict(x_input, verbose=0)
            # print("{} day output {}".format(i,yhat))
            temp_input.extend(yhat[0].tolist())
            temp_input = temp_input[1:]  ## after adding the new predicted value remove the first value of temp_input ex: if n_step=3 and  temp_input = [100,120,130], y_hat = [140], new temp_input = [120,130,140]
            # print(temp_input)
            lst_output.extend(yhat.tolist())
            i = i + 1
        else:  ## for the first prediction
            x_input = x_input.reshape((1, n_steps, 1))
            yhat = model.predict(x_input, verbose=0)
            # print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            # print(len(temp_input))
            lst_output.extend(yhat.tolist())  ## taking only output values for plotting
            i = i + 1

    # print(lst_output)
    return lst_output


def forecast_stock(tickr):
    model_file = '_'.join(tickr.split('.')) + '_model.h5'
    scaler_file = '_'.join(tickr.split('.')) + '_scaler.pkl'
    # scaler2 = load(open('/content/gdrive/My Drive/Colab Notebooks/Nifty_data/' + scaler_file, 'rb'))  ## load the saved stock scaler
    # model2 = load_model('/content/gdrive/My Drive/Colab Notebooks/Nifty_data/' + model_file)  ## load the saved model
    scaler2 = load(open('scalers/' + scaler_file, 'rb'))  ## load the saved stock scaler
    model2 = load_model('lstm_models/' + model_file)  ## load the saved model

    ## retreive the last 100 days closing prices(timestep for model input)
    ticker = yf.Ticker(tickr)
    tcs2_df = ticker.history(period="100d")
    tcs2_df['Date'] = tcs2_df.index  ## apply date transformation to string
    tcs2_df.reset_index(drop=True)
    tcs2_df['Date'] = tcs2_df['Date'].apply(lambda x: str(x.date()))

    ## scale the closing prices with the scaler for the trained model
    scaled_val = scaler2.transform(np.array(tcs2_df['Close'].values).reshape(-1, 1))
    scaled_val = scaled_val.reshape(1, -1)
    temp_scaled = list(scaled_val)
    temp_scaled = temp_scaled[0].tolist()

    ## get the predicted values for the next 30 days
    fst_output = predict_future(temp_scaled, scaled_val, model2)

    ## generate the dates for predited values
    startdate = date.today() + timedelta(days=1)
    Enddate = date.today() + timedelta(days=31)

    day_inp = tcs2_df["Date"].values
    day_pred = np.arange(str(startdate), str(Enddate), dtype="M8")
    day_pred = np.array([str(day) for day in day_pred])

    ## inverse transform the predicted values to the closing prices(before scaling)
    inverse_inp = np.array([val for val in scaler2.inverse_transform(scaled_val)[0]])
    inverse_pred = np.array([val[0] for val in scaler2.inverse_transform(fst_output)])

    ## concatenate the input prices and the forecated prices and dates
    forecast_dates = np.concatenate([day_inp, day_pred])
    forecast_prices = np.concatenate([inverse_inp, inverse_pred])

    return day_inp, inverse_inp, day_pred, inverse_pred
    # return forecast_dates,forecast_prices



# forecast_dates,forecast_prices = forecast_stock('TCS.NS')
# # print(forecast_dates)
# # print(forecast_prices)
# forecast_dict = {date:price for date,price in zip(forecast_dates,forecast_prices)}
# print(forecast_dict)


