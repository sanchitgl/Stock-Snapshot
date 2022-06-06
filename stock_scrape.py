import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

page = requests.get('https://roic.ai/financials/AAPl')
soup = BeautifulSoup(page.content, 'html.parser')
page_body = soup.body

def scrape_values(text):
    values = []
    rule = str(text + '</span>(.*?)<span')
    text = re.search(rule,str(page_body)).group(1)
    soup2= BeautifulSoup(text, 'html.parser')
    result = soup2.find_all("div", {"class":"w-[80px] select-none pr-1 grow text-right text-xs 2xl:text-sm font-medium"})
    for r in result:
        values.append(r.text)
    return values 

def scrape_dates():
    year = []
    text = re.search(r'in millions</span>(.*?)<span',str(page_body)).group(1)
    #print(text)
    soup3= BeautifulSoup(text, 'html.parser')
    result = soup3.find_all("div", {"class":"w-[80px] select-none bg-white pr-1 grow font-light text-right text-sm text-neutral-400"})
    #print(result)
    for r in result:
        year.append(r.text)
    return year

df = pd.DataFrame()

df['Year'] = pd.Series(scrape_dates())
df['Revenue'] = pd.Series(scrape_values('Revenue'))
df['Net_inc'] = pd.Series(scrape_values('Net Income'))
df['Free Cash Flow'] = pd.Series(scrape_values('Free Cash Flow'))

print(df)
#print(result)
#print(text)
#print(spans)
# for span in spans:
#     if 'Free Cash Flow' in span:
#         #print(span) 
# paras = soup.find('span').findAllNext()

# for node in soup.findAll(['span', 'div']):
#     if node.name == 'span':
#         genre = node.text
#         #print(genre)
#     elif 'w-[80px] select-none pr-1 grow text-right text-xs 2xl:text-sm font-medium' in node.get('class', ''):
#         #print([genre, node.text])
#         #elif 'gig-title' in node.get('class', ''):
#         #    yield genre, node.text

#print(all_span_tags)
#print(title)
#print("###########")
#print(paras)
#print(page_body)
#print(res.status_code)