import streamlit as st
#from StockApi_data import *
from Stock_scrape_dcf import *
import re
import altair as alt
from functools import reduce
from PIL import Image
#import plotly.express as px

def landing_page():
    img = Image.open('images/7b5298e4cd264eb283b80da981337b58.png')
    st.set_page_config(
     page_title="Stock Snapshot",
     page_icon=img,
     layout="wide")

    logo, title = st.columns([1,4])
    with logo:
        st.image(img)
    with title:
        st.title(" Your One-stop Stock Analysis Tool")
        st.subheader("Access to 20 Years of Financial data and Intrinsic value Calculation! ")
    st.info("Quarterly data and charts are coming soon!")
    st.sidebar.markdown("# Stock Overview") 
    st.sidebar.markdown("Get 20 year+ financial data and charts on relevant metrics")
    st.write('##')
    st.sidebar.markdown("Quarterly Data and charts are coming soon!")
    #st.title("Investment Buddy")
    #st.subheader("Get a Financial overview of companies and their intrinsic value!")
    submit, tckr = get_stock_tickr()
    print(tckr)

    if submit == True:
        print(tckr)
        try:
            quote, df_inc, df_bal, df_cash = get_financials(tckr)
        except:
            st.warning("Sorry, wrong ticker symbol. Try 'AAPL', 'MSFT' or 'NFLX'")
            st.stop()
        #st.write(df_inc)
        #st.write(df_bal)
        #st.write(df_cash)
        data_frames = [df_inc, df_bal, df_cash]
        data = reduce(lambda  left,right: pd.merge(left,right,on=['date'],
                                            how='outer'), data_frames)
        #st.write(data)
        #
        st.header(quote['Name']+' financial overview')
        st.write("##")
        rev, net_inc, fcf = st.columns(3)
        debt_eq, cash, shares_out, = st.columns(3)
        with rev:
            #st.subheader('Revenue')
            plot_bar_chart(data,'date','Revenue','Revenue (mill)')
            with st.expander("Percent change YoY"):
                plot_change_chart(data,'date','Revenue')
        with net_inc:
            #st.subheader('Net Income')
            plot_bar_chart(data,'date','Net_inc','Net Income (mill)')
            with st.expander("Percent change YoY"):
                plot_change_chart(data,'date','Net_inc')
        with fcf:
            #st.subheader('Free Cash Flow')
            plot_bar_chart(data,'date','Fcf','Free Cash Flow (mill)')
            with st.expander("Percent change YoY"):
                plot_change_chart(data,'date','Fcf')
        with debt_eq:
            #st.subheader('Debt/Equity')
            plot_bar_chart2(data,'date','Debt_eq','Debt/Equity')
        with cash:
            #st.subheader('Cash & Equivalents')
            plot_bar_chart2(data,'date','net_cash','Cash - Tot Debt')
        with shares_out:
            #st.subheader('Shares Outstanding')
            plot_bar_chart2(data,'date','shares_out','Shares Outstanding (mill)')
        
        st.write('# Financials')

        st.subheader('Income Statement')
        df_1 = process_df(df_inc)
        st.dataframe(df_1, width=1200)

        st.subheader('Balance Sheet')
        df_bal['Debt_eq'] = df_bal['Debt_eq'].round(2)
        df_bal.pop('net_cash')
        df_2 = process_df(df_bal)
        st.dataframe(df_2, width=1200)

        st.subheader('Cash Flow Statement')
        df_3 = process_df(df_cash)
        st.dataframe(df_3, width=1200)
        #st.table(data.T)

def process_df(df):
    df.index = df['date']
    df.rename(columns = {'Net_inc':'Net Income', 'Fcf':'Free Cash FLow',
                            'Debt_eq':'Debt/Equity', 'st_debt':'Short Term Debt', 'lg_debt':'Long Term Debt', 
                            'shares_out':'Shares Outstanding', 'cash_eq':'Cash & Equivalents', 'st_equity':'Shareholder\'s Equity'}, inplace = True)
    df.pop('date')
    df = df.T
    df.fillna('--', inplace=True)
    df = df.applymap(str)
    return df

def plot_change_chart(data,X,Y):
    #data['changeYoY'] = data[Y].diff() / data[Y].abs().shift()
    data['changeYoY'] = (data[Y].diff() / data[Y].abs().shift())*100
    #print(data['changeYoY'])

    chart = (alt.Chart(data).mark_line(point = True).encode(
    x=alt.X(X, type="nominal", title=""),
    y=alt.Y('changeYoY',type="quantitative"#, axis=alt.Axis(format='%')
    , title=""),
    color=alt.value("#aec7e8"),
    tooltip = [alt.Tooltip('changeYoY', title='',format='.1f')]
    )).interactive()
    line = (alt.Chart(data).mark_line(point = True).transform_window(
        # The field to average
        rolling_mean='mean(changeYoY)',
        # The number of values before and after the current value to include.
        frame=[-2, 0]
        ).encode(
        x=alt.X(X, type="nominal", title=""),
        y='rolling_mean:Q',
        color=alt.value("#ffbb78"),
        tooltip = [alt.Tooltip('rolling_mean:Q', title='3 Yr Avg',format='.1f')]
        )).interactive()
    change_chart = (chart + line).interactive()
    st.altair_chart(change_chart, use_container_width=True)

def plot_bar_chart2(data,X,Y,T):
    chart = (
        alt.Chart(data, title=T).configure_title(fontSize=20)
        .mark_bar()
        .encode(
            x=alt.X(X, type="nominal", title=""),
            y=alt.Y(Y, type="quantitative", title=""),
            color=alt.condition(
            alt.datum[Y] > 0,
            alt.value("#74c476"),  # The positive color
            alt.value("#d6616b")  # The negative color
            ),
            tooltip = [alt.Tooltip(Y, title=T,format='.1f')]
            #color=alt.Color("variable", type="nominal", title=""),
            #order=alt.Order("variable", sort="descending"),
        )
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_bar_chart(data,X,Y,T):
    bar = (
        alt.Chart(data, title=T)
        .mark_bar()
        .encode(
            x=alt.X(X, type="nominal", title=""),
            y=alt.Y(Y, type="quantitative", title=""),
            color=alt.condition(
            alt.datum[Y] > 0,
            alt.value("#74c476"),  # The positive color
            alt.value("#d6616b")  # The negative color
            ),
            tooltip = [alt.Tooltip(Y, title=T)]
            #color=alt.Color("variable", type="nominal", title=""),
            #order=alt.Order("variable", sort="descending"),
        )
    )
    line = alt.Chart(data).mark_line(point = True).transform_window(
        # The field to average
        rolling_mean='mean('+Y+')',
        # The number of values before and after the current value to include.
        frame=[-2, 0]
        ).encode(
        x=alt.X(X, type="nominal", title=""),
        y='rolling_mean:Q',
        color=alt.value("#636363"),
        opacity= alt.value(0.7),
        tooltip = [alt.Tooltip('rolling_mean:Q', title='3 Yr Avg',format='.1f')]
        )

    chart = (bar + line).configure_title(fontSize=20)

    st.altair_chart(chart, use_container_width=True)


def get_stock_tickr():
    with st.form(key = 'ticker', clear_on_submit=False):
        ticker, submit  = st.columns([3,1])
        with ticker:
            tckr = st.text_input('Stock Ticker')
        with submit:
            st.write("##")
            submit_request = st.form_submit_button(label = 'Submit')

    return submit_request, tckr


landing_page() 