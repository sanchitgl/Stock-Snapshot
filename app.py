import streamlit as st
#from StockApi_data import *
from Stock_scrape_dcf import *
import re
import altair as alt
#import plotly.express as px

def landing_page():
    st.set_page_config(layout="wide")
    st.title("Investment Buddy")
    st.subheader("Get a Financial overview of companies and their intrinsic value!")
    st.write("##")
    submit, tckr, growth, sl, dr = get_stock_tickr()
    print(tckr)

    if submit == True:
        try:
            quote, data, dcf_value = main(tckr, growth, sl, dr)
        except:
            st.warning("Sorry, wrong ticker symbol. Try 'AAPL', 'MSFT' or 'NFLX'")
            st.stop()
        #data, dcf_value = main(tckr, growth, sl, dr)
        #st.dataframe(data)
        st.header(quote['Name']+' financial overview')
        st.write("##")
        rev, net_inc, fcf = st.columns(3)
        debt_eq, cash, shares_out, = st.columns(3)
        with rev:
            #st.subheader('Revenue')
            plot_bar_chart(data,'date','Revenue','Revenue (mill)')
            with st.expander("Percent chnage YoY"):
                plot_change_chart(data,'date','Revenue')
        with net_inc:
            #st.subheader('Net Income')
            plot_bar_chart(data,'date','Net_inc','Net Income (mill)')
            with st.expander("Percent chnage YoY"):
                plot_change_chart(data,'date','Net_inc')
        with fcf:
            #st.subheader('Free Cash Flow')
            plot_bar_chart(data,'date','Fcf','Free Cash Flow (mill)')
            with st.expander("Percent chnage YoY"):
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

        st.header('Valuation')
        
        if dcf_value != 'NA' and dcf_value >= 0:
            if 'T' in quote['MarketCapitalization']:
                quote['MarketCapitalization'] = re.sub(r'T', '', quote['MarketCapitalization'])
                quote['MarketCapitalization'] = 1000000*float(quote['MarketCapitalization'])
            elif 'B' in quote['MarketCapitalization']:
                quote['MarketCapitalization'] = re.sub(r'B', '', quote['MarketCapitalization'])
                quote['MarketCapitalization'] = 1000*float(quote['MarketCapitalization'])
            #quote['MarketCapitalization'] = re.sub(r'T', '000000', quote['MarketCapitalization'])
            #quote['MarketCapitalization'] = re.sub(r'B', '000000', quote['MarketCapitalization'])

            val_data = [['MCap',quote['MarketCapitalization']],['DCF Value',dcf_value]]
            #val_df = val_df.set_index
            val_df = pd.DataFrame(val_data, columns=['Label', 'Value'])
            #val_df = val_df.set_index('Label')

            #print(val_df)
            #plot_bar_chart(val_df)
            plot_val_chart(val_df,'Value','Label')
            #st.bar_chart(val_df)
            st.write("DCF Valuation:  "+str(int(dcf_value)))
            st.write("Current MCap:  "+str(int(quote['MarketCapitalization'])))
            
            margin_of_safety = int(((dcf_value-quote['MarketCapitalization'])/quote['MarketCapitalization'])*100)
            if margin_of_safety <= 0:
                st.write(f'<b style="color:#d6616b">{"Margin of Safety:  "+str(margin_of_safety)+"%"}</b>', unsafe_allow_html=True)
            else:
                st.write(f'<b style="color:#74c476">{"Margin of Safety:  "+str(margin_of_safety)+"%"}</b>', unsafe_allow_html=True)
            #st.write("Margin of Safety : "+str(margin_of_safety)+"%")
        else:
            st.warning("Sorry, DCF Calculation doesn't work on loss making companies.")
        
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

def plot_val_chart(data,x,y):
    # Horizontal stacked bar chart
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(x, type="quantitative", title=""),
            y=alt.Y(y, type="nominal", title=""),
            color=alt.Color(y, type="nominal", title=""),
            #order=alt.Order("variable", sort="descending"),
        ).properties(height=200)
    )

    st.altair_chart(chart, use_container_width=True)


def get_stock_tickr():
    with st.form(key = 'ticker', clear_on_submit=False):
        ticker, submit  = st.columns([3,1])
        gr_avg, text, gr_num, slowdown, discount = st.columns([1,0.15,1,1,1])
        with ticker:
            tckr = st.text_input('Stock ticker')
        with gr_avg:
            gr_avg = st.selectbox('Infer Growth rate',('Select','3yr Avg','5yr Avg'))
        with text:
            st.write("##")
            st.text(" OR ")
        with gr_num:
            gr_num = st.number_input('Input Growth rate', 0.0, 100.0, 12.0, 0.5, help = 'Growth rate for next 10 years \nlow: 5 \nmoderate: 10 \nhigh: 15')
        with slowdown:
            sl = st.number_input('Slowdown rate YoY', 0.0, 100.0, 0.5,0.5)
        with discount:
            dr = st.number_input('Discount rate', 0.0, 100.0, 13.5,0.5)
        with submit:
            st.write("##")
            submit_request = st.form_submit_button(label = 'Submit')
        if gr_avg != 'Select':
            growth = gr_avg
        else:
            growth = gr_num
    return submit_request, tckr, growth, sl, dr 

landing_page() 