import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

def scrape_values(text,page_body):
    values = []
    rule = str(text + '</span>(.*?)<span')
    text = re.search(rule,str(page_body)).group(1)
    soup2= BeautifulSoup(text, 'html.parser')
    result = soup2.find_all("div", {"class":"w-[80px] select-none pr-1 grow text-right text-xs 2xl:text-sm font-medium"})
    for r in result:
        values.append((r.text).replace('- -','NA').replace(',','').replace('(','-').replace(')',''))
    return values 

def scrape_values2(text,page_body):
    values = []
    rule = str(text + '</span>(.*?)<span')
    text = re.search(rule,str(page_body)).group(1)
    #print(text)
    soup2= BeautifulSoup(text, 'html.parser')
    result = soup2.find_all("div", {"class":"w-[80px] select-none pr-1 grow text-right text-xs 2xl:text-sm font-light"})
    #print("----------------------------")
    #print(result)
    for r in result:
        values.append((r.text).replace('- -','NA').replace(',','').replace('(','-').replace(')',''))
    return values 

def scrape_dates(page_body):
    year = []
    text = re.search(r'in millions</span>(.*?)<span',str(page_body)).group(1)
    #print(text)
    soup3= BeautifulSoup(text, 'html.parser')
    result = soup3.find_all("div", {"class":"w-[80px] select-none bg-white pr-1 grow font-light text-right text-sm text-neutral-400"})
    #print(result)
    for r in result:
        year.append(r.text)
    return year

def scrape_quote(text, page_body):
    rule = str(text+'</span>(.*?)</span>')
    text = re.search(rule,str(page_body)).group(1)
    #print(text)
    soup2= BeautifulSoup(text, 'html.parser')
    result = soup2.find("span", {"class":"block text-lg font-light"})
    #print(result)

    return result.text

def get_financials(stock_ticker):
    page = requests.get('https://roic.ai/financials/'+stock_ticker)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(soup)
    #st.text(soup)
    page_body = soup.body
    print(page_body)
     
    name = soup.find('title')
    company_name = name.string.split('·')[0]

    df_inc = pd.DataFrame()

    df_inc['date'] = pd.to_numeric(pd.Series(scrape_dates(page_body)),errors= 'coerce')
    df_inc['Revenue'] = pd.to_numeric(pd.Series(scrape_values('Revenue',page_body)),errors= 'coerce')
    df_inc['COGS'] = pd.to_numeric(pd.Series(scrape_values2('>COGS',page_body)),errors= 'coerce')
    df_inc['Gross Profit'] = pd.to_numeric(pd.Series(scrape_values('Gross Profit',page_body)),errors= 'coerce')
    df_inc['Operating Income'] = pd.to_numeric(pd.Series(scrape_values('Operating Income',page_body)),errors= 'coerce')
    df_inc['Net_inc'] = pd.to_numeric(pd.Series(scrape_values('Net Income',page_body)),errors= 'coerce')
    df_inc['shares_out']= pd.to_numeric(pd.Series(scrape_values2('Weighted Avg. Shares Outs.',page_body)),errors= 'coerce')
    df_inc['EPS'] = pd.to_numeric(pd.Series(scrape_values2('EPS',page_body)),errors= 'coerce')

    df_bal = pd.DataFrame()
    df_bal['date'] = pd.to_numeric(pd.Series(scrape_dates(page_body)),errors= 'coerce')
    df_bal['cash_eq']= pd.to_numeric(pd.Series(scrape_values2('Cash \&amp\; Short-Term Investments',page_body)),errors= 'coerce')
    df_bal['Total Current Assets']= pd.to_numeric(pd.Series(scrape_values('Total Current Assets',page_body)),errors= 'coerce')
    df_bal['Total Non-Current Assets']= pd.to_numeric(pd.Series(scrape_values2('Total Non-Current Assets',page_body)),errors= 'coerce')
    df_bal['Total Assets']= pd.to_numeric(pd.Series(scrape_values('Total Assets',page_body)),errors= 'coerce')
    df_bal['st_debt']= pd.to_numeric(pd.Series(scrape_values2('>Short\-Term Debt',page_body)),errors= 'coerce')
    df_bal['Total Current Liabilities']= pd.to_numeric(pd.Series(scrape_values('Total Current Liabilities',page_body)),errors= 'coerce')
    df_bal['lg_debt']= pd.to_numeric(pd.Series(scrape_values2('Long\-Term Debt',page_body)),errors= 'coerce')
    df_bal['Total Non-Current Liabilities']= pd.to_numeric(pd.Series(scrape_values2('Total Non-Current Liabilities',page_body)),errors= 'coerce')
    df_bal['Total Liabilities']= pd.to_numeric(pd.Series(scrape_values('Total Liabilities',page_body)),errors= 'coerce')
    df_bal['Retained Earnings']= pd.to_numeric(pd.Series(scrape_values2('Retained Earnings',page_body)),errors= 'coerce')
    df_bal['st_equity']= pd.to_numeric(pd.Series(scrape_values('Total Stockholders Equity',page_body)),errors= 'coerce')
    df_bal['Debt_eq']= (df_bal['lg_debt'].fillna(0)+df_bal['st_debt'].fillna(0))/df_bal['st_equity']
    df_bal['net_cash']= df_bal['cash_eq'] -(df_bal['st_debt'].fillna(0)+df_bal['lg_debt'].fillna(0))

    df_cash = pd.DataFrame()
    df_cash['date'] = pd.to_numeric(pd.Series(scrape_dates(page_body)),errors= 'coerce')
    df_cash['Cash From Operations'] = pd.to_numeric(pd.Series(scrape_values('Cash Provided by Operating Activities',page_body)),errors= 'coerce')
    df_cash['CAPEX'] = pd.to_numeric(pd.Series(scrape_values2('CAPEX',page_body)),errors= 'coerce')
    df_cash['Fcf'] = pd.to_numeric(pd.Series(scrape_values('Free Cash Flow',page_body)),errors= 'coerce')
    df_cash['Acquisitions Net'] = pd.to_numeric(pd.Series(scrape_values2('Acquisitions Net',page_body)),errors= 'coerce')
    df_cash['Cash Used-Investing Act'] = pd.to_numeric(pd.Series(scrape_values('Cash Used for Investing Activities',page_body)),errors= 'coerce')
    df_cash['Debt Repayment'] = pd.to_numeric(pd.Series(scrape_values2('Debt Repayment',page_body)),errors= 'coerce')
    df_cash['Stock Issued'] = pd.to_numeric(pd.Series(scrape_values2('Common Stock Issued',page_body)),errors= 'coerce')
    df_cash['Stock Repurchased'] = pd.to_numeric(pd.Series(scrape_values2('Common Stock Repurchased',page_body)),errors= 'coerce')
    df_cash['Dividends'] = pd.to_numeric(pd.Series(scrape_values2('Dividends Paid',page_body)),errors= 'coerce')
    df_cash['Cash by Financing Act'] = pd.to_numeric(pd.Series(scrape_values('Cash Used/Provided by Financing Activities',page_body)),errors= 'coerce')
    df_cash['Net Change in Cash'] = pd.to_numeric(pd.Series(scrape_values('Net Change In Cash',page_body)),errors= 'coerce')


    df_inc = df_inc.loc[df_inc['date']>= 2002]
    df_bal = df_bal.loc[df_bal['date']>= 2002]
    df_cash = df_cash.loc[df_cash['date']>= 2002]

    quote = {'MarketCapitalization':str(scrape_quote('>P/E to S\&amp\;P500',page_body)),
                'Name' : company_name }
    # df.index = pd.to_datetime(df.index).year
    # df['date'] = df.index 
    #print(df.index)
    return quote, df_inc, df_bal, df_cash

def get_quote(stock_ticker):
    page = requests.get('https://roic.ai/financials/'+stock_ticker)
    soup = BeautifulSoup(page.content, 'html.parser')
    page_body = soup.body
     
    name = soup.find('title')
    company_name = name.string.split('·')[0]

    NI = pd.to_numeric(pd.Series(scrape_values('Net Income',page_body)),errors= 'coerce')
    NI = list(NI)
    FCF = pd.to_numeric(pd.Series(scrape_values('Free Cash Flow',page_body)),errors= 'coerce')
    FCF = list(FCF)
    st_debt = pd.to_numeric(pd.Series(scrape_values2('>Short\-Term Debt',page_body)),errors= 'coerce')
    lg_debt = pd.to_numeric(pd.Series(scrape_values2('Long\-Term Debt',page_body)),errors= 'coerce')
    cash_eq = pd.to_numeric(pd.Series(scrape_values2('Cash \&amp\; Short-Term Investments',page_body)),errors= 'coerce')
    net_debt_list = list((st_debt.fillna(0)+ lg_debt.fillna(0))- cash_eq)
    net_debt = net_debt_list[-1]
    #print(net_debt)
    quote = {'MarketCapitalization':str(scrape_quote('>P/E to S\&amp\;P500',page_body)),
                'Name' : company_name }
    return NI, FCF, net_debt, quote


# def main(company_ticker):
#     quote, data = get_financials(company_ticker)
#     #print("---------")
#     #print(data.index)
#     fcf = list(data['Fcf'])
#     NI = list(data['Net_inc'])

#     # if fcf[-1] > 0:
#     #     int_value = DCFvalue(fcf, growth, sl/100, dr/100)
#     # elif NI[-1] >0:
#     #     int_value = DCFvalue(NI, growth, sl/100, dr/100)
#     # else:
#     #     int_value = 'NA'

#     return quote, data
        
#quote, df = get_financials('BABA')