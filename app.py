# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask,request
import yfinance as yf
import requests
from flask_cors import CORS
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId

# Flask constructor takes the name of
# current module (__name__) as argument.
import lstm_predict

client = pymongo.MongoClient("localhost", 27017)
db = client.stocks

app = Flask(__name__)
CORS(app)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/stocklist',methods=['GET','POST'])
def list_stocks():
    it_df = yf.download(tickers="TCS.NS INFY.NS WIPRO.NS MARUTI.NS APOLLOHOSP.NS ADANIPOWER.NS ITC.NS HDFC.NS LT.NS TATAPOWER.NS NTPC.NS", period="1mo")
    it_df.index = it_df.index.astype('str')
    json_data = it_df['Close'].to_json()
    return json_data


@app.route('/stockdetail/<tickr>',methods=['GET'])
def stock_details(tickr):
    it_df = yf.download(tickers=tickr, period="1mo")
    it_df.index = it_df.index.astype('str')
    final_json={}
    final_json["Close"]=it_df["Close"].to_dict()
    final_json["low"]=min(it_df["Low"])
    final_json["high"]=max(it_df["High"])
    final_json["volume"]=max(it_df["Volume"])
    return final_json


@app.route('/stockforecast/<tickr>',methods=['GET'])
def stock_forecast(tickr):
    day_inp, inverse_inp, day_pred, inverse_pred = lstm_predict.forecast_stock(tickr)
    forecast_dict = {date:price for date,price in zip(day_inp,inverse_inp)}
    forecastpre_dicgt = {date:price for date,price in zip(day_pred,inverse_pred)}
    dict={
        "past":forecast_dict,
        "future":forecastpre_dicgt
    }
    return dict

@app.route('/stockorder',methods=['POST'])
def upload_order():
    json=request.json
    stock={
        "symbol":json.get("symbol"),
        "shares":json.get("shares"),
        "gainloss":json.get("gainloss"),
        "boughtPrice":json.get("boughtPrice")
    }
    userd={
        "name":json.get("name")
    }
    data=db.users.find_one(userd)
    cur=data.get("currency")
    if cur<json.get("boughtPrice"):
        return "Error"
    cur=cur-json.get("boughtPrice")
    data["currency"]=cur
    print(data)
    print(stock)
    db.orders.insert_one(stock)
    db.users.replace_one(userd,data,True)
    return "Uploaded"

@app.route('/stockorders',methods=['GET'])
def get_orders():
    data=db.orders.find()
    list_cur = list(data)
    json_data = dumps(list_cur)
    print(json_data)
    return json_data

@app.route('/stockorder',methods=['DELETE'])
def delete_orders():
    json=request.json
    data=db.orders.find_one({"_id":ObjectId(json.get("id"))})

    it_df = yf.download(tickers=data.get("symbol"), period="1mo")
    it_df.index = it_df.index.astype('str')
    final_json={}
    final_json["Close"]=it_df["Close"].to_dict()
    price=0.0
    for i in final_json["Close"].values():
        price=i 
    shares_count=int(data.get("shares"))
    tot=price*shares_count
    userd={
        "name":json.get("name")
    }
    data=db.users.find_one(userd)
    print(data,"user")
    data["currency"]+=tot
    print(data)
    db.orders.find_one_and_delete({"_id":ObjectId(json.get("id"))})
    db.users.replace_one(userd,data,True)
    return "Deleted"

@app.route('/user',methods=['POST'])
def get_user():
    json=request.json
    data=db.users.find_one({"name":json.get("name")})
    print(json)
    print(data)
    if data==None:
        db.users.insert_one(json)
        data=db.users.find_one({"name":json.get("name")})
    dict={
        "name":data.get("name"),
        "currency":data.get("currency")
    }
    return dict



# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()