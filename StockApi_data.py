#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 12:59:37 2020
@author: sanchit
"""
import http.client, urllib.request, urllib.parse, urllib.error, base64
import numpy as np
#import numpy_financial as npf
import pandas as pd
import requests, json 
import pprint 

def get_financials(company_ticker):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': 'dbf096045ab64e51b0b81940520e6a93',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'formType': '10-K',
        'filingOrder': '0',
    })

    # change ticker 'aapl' to the required company
    #company_ticker = 'aapl'


    try:
        conn = http.client.HTTPSConnection('services.last10k.com')
        conn.request("GET", "/v1/company/"+company_ticker+"/ratios?%s" % params, "{body}", headers)
        response = conn.getresponse()
        ratio_data = response.read()
        conn.request("GET", "/v1/company/"+company_ticker+"/quote?%s" % params, "{body}", headers)
        response = conn.getresponse()
        quote_data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    #convverting data into dict
    stock_data = json.loads(ratio_data)
    stock_quote = json.loads(quote_data)
    print("********")
    #print(stock_quote)
    #storing useful data in main_data
    main_data = stock_data['data']['attributes']['result']
    main_quote = stock_quote['data']['attributes']['result']

    print(main_data)

    #stock_quote = pd.DataFrame()
    df = pd.DataFrame()

    #df['Dates'] = main_data['Revenue']['Historical'].keys()
    df['Revenue'] = pd.Series(main_data['Revenue']['Historical'])
    df['Net_inc'] = pd.Series(main_data['NetIncome']['Historical'])
    df['Fcf'] = pd.Series(main_data['FreeCashFlow']['Historical'])
    df['Debt_eq'] = pd.Series(main_data['DebtEquity']['Historical'])
    df['st_debt'] = pd.Series(main_data['ShortTermDebt']['Historical'])
    df['lg_debt'] = pd.Series(main_data['LongTermDebt']['Historical'])
    df['shares_out'] = pd.Series(main_data['Shares']['Historical'])
    df['cash_eq'] = pd.Series(main_data['CashAndShortTermInvestments']['Historical'])
    df['net_cash'] = df['cash_eq'] -(df['st_debt'].fillna(0)+df['lg_debt'].fillna(0))

    #Printing the required data
    #pprint.pprint(main_data['FreeCashFlow'])
    #pprint.pprint(main_data['CurrentRatio'])
    df.index = pd.to_datetime(df.index).year
    df['date'] = df.index 
    #print(df.index)
    return main_quote,df

def AvgGrowth(x, growth):
    if growth == '3yr Avg':
        rate = ((x[-1]/x[-4])**(1/3))-1
        if rate <= 0.4:
            growth_rate = rate
        else:
            growth_rate = 0.4
    elif growth == '5yr Avg':
        rate = ((x[-1]/x[-6])**(1/5))-1
        if rate <= 0.4:
            growth_rate = rate
        else:
            growth_rate = 0.4
    return growth_rate
    
def CAGR(fcf):
    cagr = (fcf[-1]/fcf[0])**(1/(len(fcf)-1))-1
    return cagr

def DCFvalue(x,growth,margin,discount):
    fcf = (x[-3]+x[-2]+x[-1])/3
    if growth in ['3yr Avg','5yr Avg']:
        totgrowth = AvgGrowth(x,growth)
        print(totgrowth)
    else:
        totgrowth = growth/100
    totfcf = []
    n = 0
    while totgrowth>0.02 and n <10:
        if fcf <= 0:
            fcf_growth = (-1)*(fcf*(totgrowth))
            fcf = fcf + fcf_growth
        else:
            fcf = fcf*((1+totgrowth))
        totfcf.append(fcf)
        totgrowth = totgrowth-margin       
        n += 1
    npv = get_npv(discount,totfcf)
    if totgrowth <= 0.05:
        terminal_value = totfcf[-1]/(discount- totgrowth)
    else:
        terminal_value = totfcf[-1]/(discount- 0.05)
    total_npv = npv+terminal_value
    #total_npv = terminal_value
    return total_npv

def get_npv(rate, values):
    values = np.asarray(values)
    return (values / (1+rate)**np.arange(1,len(values)+1)).sum(axis=0)

def main(company_ticker, growth, sl, dr):
    quote, data = get_financials(company_ticker)
    #print("---------")
    #print(data.index)
    fcf = list(data['Fcf'])
    NI = list(data['Net_inc'])
    avg_fcf_3 = (fcf[-3]+fcf[-2]+fcf[-1])/3
    avg_NI_3 = (NI[-3]+NI[-2]+NI[-1])/3

    if avg_fcf_3 > 0:
        int_value = DCFvalue(fcf, growth, sl/100, dr/100)
    elif avg_NI_3 >0:
        int_value = DCFvalue(NI, growth, sl/100, dr/100)
    else:
        int_value = 'NA'

    return quote, data, int_value
        
    
    
        
    