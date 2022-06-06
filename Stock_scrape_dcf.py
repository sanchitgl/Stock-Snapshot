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
    page_body = soup.body
     
    name = soup.find('title')
    company_name = name.string.split('·')[0]

    df = pd.DataFrame()

    df['date'] = pd.to_numeric(pd.Series(scrape_dates(page_body)),errors= 'coerce')
    df['Revenue'] = pd.to_numeric(pd.Series(scrape_values('Revenue',page_body)),errors= 'coerce')
    df['Net_inc'] = pd.to_numeric(pd.Series(scrape_values('Net Income',page_body)),errors= 'coerce')
    df['Fcf'] = pd.to_numeric(pd.Series(scrape_values('Free Cash Flow',page_body)),errors= 'coerce')
    df['st_debt']= pd.to_numeric(pd.Series(scrape_values2('>Short\-Term Debt',page_body)),errors= 'coerce')
    df['lg_debt']= pd.to_numeric(pd.Series(scrape_values2('Long\-Term Debt',page_body)),errors= 'coerce')
    df['cash_eq']= pd.to_numeric(pd.Series(scrape_values2('Cash \&amp\; Short-Term Investments',page_body)),errors= 'coerce')
    df['st_equity']= pd.to_numeric(pd.Series(scrape_values('Total Stockholders Equity',page_body)),errors= 'coerce')
    df['Debt_eq'] = (df['lg_debt']+df['st_debt'])/df['st_equity']
    df['net_cash'] = df['cash_eq'] -(df['st_debt'].fillna(0)+df['lg_debt'].fillna(0))
    df['shares_out']= pd.to_numeric(pd.Series(scrape_values2('Weighted Avg. Shares Outs.',page_body)),errors= 'coerce')

    df = df.loc[df['date']>= 2000]

    quote = {'MarketCapitalization':str(scrape_quote('>P/E to S\&amp\;P500',page_body)),
                'Name' : company_name }
    # df.index = pd.to_datetime(df.index).year
    # df['date'] = df.index 
    #print(df.index)
    return quote, df

def AvgGrowth(x, growth):
    if growth == '3yr Avg':
        rate = ((x[-1]/x[-4])**(1/3))-1
        print(rate)
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
    while totgrowth>0 and n <10:
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

    if fcf[-1] > 0:
        int_value = DCFvalue(fcf, growth, sl/100, dr/100)
    elif NI[-1] >0:
        int_value = DCFvalue(NI, growth, sl/100, dr/100)
    else:
        int_value = 'NA'

    return quote, data, int_value
        
#quote, df = get_financials('BABA')