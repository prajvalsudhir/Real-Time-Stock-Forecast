# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask
import yfinance as yf
import requests

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/stocklist',methods=['GET','POST'])
def list_stocks():
    it_df = yf.download(tickers="TCS.NS INFY.NS WIPRO.NS MARUTI.NS APOLLOHOSP.NS", period="1mo")
    it_df.index = it_df.index.astype('str')
    json_data = it_df['Close'].to_json()
    return json_data


@app.route('/stockdetail/<tickr>',methods=['GET'])
def stock_details(tickr):
    it_df = yf.download(tickers=tickr, period="1mo")
    it_df.index = it_df.index.astype('str')
    json_data = it_df.to_json()
    return json_data


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()