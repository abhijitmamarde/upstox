# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 10:29:35 2018

@author: Gireesh Sundaram
"""

#Importing packages
from upstox_api.api import *
from datetime import datetime, time
import time as sleep
import os
import pandas as pd
from matplotlib import pyplot as plt

#%%
api_key = "<YOUR API KEY>"
api_secret = "<YOUR API SECRET>"
redirect_uri = "<YOUR REDIRECT URI>"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(s.get_login_url())
code = "<CODE THAT YOU GET FROM URL>"

s.set_code (code)
access_token = s.retrieve_access_token()

u = Upstox (api_key, access_token)

print("Login successful. Verify profile:")
print(u.get_profile())

#%%
master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ

#Function to fetch the current available balance:
def CheckBalance():
    balance = pd.DataFrame(u.get_balance())
    balance1 = balance["equity"]["available_margin"]
    return balance1

#function to fetch historic data
def historicData(script, start_dt, end_dt):
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_1,
                      datetime.strptime(start_dt, '%d/%m/%Y').date(),
                      datetime.strptime(end_dt, '%d/%m/%Y').date()))
    data.head()
    data["sma5"] = data.cp.rolling(window=5).mean()
    data["sma50"] = data.cp.rolling(window=50).mean()
    return data

def buy(script, amount, stoploss, squareoff):
    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 1,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 amount,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def sell(script, amount, stoploss, squareoff):
    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 1,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 amount,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def SMACrossOver(ScriptData):
    if ScriptData.sma5.iloc[-6] < ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] < ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] < ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] < ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] > ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] > ScriptData.sma50.iloc[-1]:
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.high.iloc[-1] * 1.01), 0))
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.low.iloc[-1] * 0.99), 0))
        print("Buying at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        buy(script, ScriptData.cp.iloc[-1], stoploss, squareoff)
        
    if ScriptData.sma5.iloc[-6] > ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] > ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] > ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] > ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] < ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] < ScriptData.sma50.iloc[-1]:
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.high.iloc[-1] * 1.01), 0))
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.low.iloc[-1] * 0.99), 0))
        print("Selling at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        sell(script, ScriptData.cp.iloc[-1], stoploss, squareoff)
        
        
#%%
def CheckTrades():
    now = datetime.now()
    now_time = now.time()
    
    print("Now checking trades at: %s" %s)
    
    if time(10,11) <= now_time <= time(14,00) and CheckBalance() > 1500:
        bucket = ["APOLLOTYRE","AXISBANK","BHARTIARTL", "INDIACEM", "JETAIRWAYS",
                    "JINDALSTEL","L&TFH", "RELIANCE","SBIN", "TATAMOTORS"]
        
        for script in bucket:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" %now_time)
            print("Checking for 50 min 5min MA Crossover for %s" % script)
            SMACrossOver(historicData(script, "19/03/2018", "19/03/2018"))
            
    elif now_time >= time(14,55):
        print("Exiting all the open position now and exiting execution")
        u.cancel_all_orders() #Cancel all open orders
        exit()

#%%
while True:
    CheckTrades()
    sleep.sleep(630)
#%%