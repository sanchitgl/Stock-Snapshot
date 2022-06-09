import streamlit as st
from dcf import *
from Stock_scrape_dcf import get_quote
from dcf import DCFvalue
import re
import altair as alt

st.markdown("# DCF Calculator")
st.sidebar.markdown(" DCF Calculator")
st.sidebar.markdown("Calculate Intrinsic value of a company through dicounted cash flow model!")
st.sidebar.markdown("If you are new to DCF, check out this [link](https://www.investopedia.com/terms/d/dcf.asp) to read about it more.")

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

def dcf_calculator():
    with st.form(key = 'dcf', clear_on_submit=False):
        ticker, discount, fcf_ni, submit  = st.columns([2,1,0.4,0.5])
        gr1_3, gr4_6, gr7_9, ter_rate = st.columns([1,1,1,1])
    with ticker:
        tckr = st.text_input('Stock Ticker')
    with gr1_3:
        gr1_3 = st.number_input('Growth 1-3 Yr', 0.0, 100.0, 12.0, 0.5, help = 'low: 5, moderate: 10, high: 15')
    with gr4_6:
        gr4_6 = st.number_input('Growth 4-6 Yr', 0.0, 100.0, 10.0, 0.5, help = 'low: 5, moderate: 10, high: 15')
    with gr7_9:
        gr7_9 = st.number_input('Growth 7-9 Yr', 0.0, 100.0, 8.0, 0.5, help = 'low: 5, moderate: 10, high: 15')
    with fcf_ni:
        fcf_ni = st.radio("",('FCF', 'NI'))
    with ter_rate:
        ter_rate = st.number_input('Terminal Growth', 0.0, 100.0, 5.0, 0.5, help = 'Terminal growth rate, Global avg: 4')
    with discount:
        dr = st.number_input('Discount rate', 0.0, 100.0, 12.5,0.5)
    with submit:
        st.write('##')
        submit_request = st.form_submit_button(label = 'Submit')

    return submit_request, tckr, gr1_3, gr4_6, gr7_9, fcf_ni, ter_rate, dr

def landing_page():
    #st.header('Valuation')
    submit, tckr, gr1_3, gr4_6, gr7_9, fcf_ni, ter_rate, discount  = dcf_calculator()

    if submit == True:
        if discount <= ter_rate:
            st.warning("Sorry, discount rate can't be less than terminal rate.'")
            st.stop()
        print(tckr)
        #st.write(submit)
        try:
            NI, FCF, net_debt, quote = get_quote(tckr)
        #print(NI, FCF, quote )
        except:
            st.warning("Sorry, wrong ticker symbol. Try 'AAPL', 'NVDA' or 'BABA'")
            st.stop()
        if fcf_ni == 'FCF':
            amt, amts, rates, npv_values, npv, terminal_value, pv_terminal_value, dcf_value = DCFvalue(FCF, gr1_3, gr4_6, gr7_9, ter_rate, discount/100, net_debt)
        else:
            amt, amts, rates, npv_values, npv, terminal_value, pv_terminal_value, dcf_value = DCFvalue(NI, gr1_3, gr4_6, gr7_9, ter_rate, discount/100, net_debt)
        #st.write(dcf_value)
        #print(dcf_value)
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

            st.write('##')
            #plot_bar_chart(val_df)
            plot_val_chart(val_df,'Value','Label')
            #st.bar_chart(val_df)
            st.write('##')
            st.write("Intrinsic Value:  &nbsp; **"+str(int(dcf_value))+' million**')

            npv_df = pd.DataFrame()
            npv_df['Year'] = ['Year 1','Year 2','Year 3','Year 4','Year 5','Year 6','Year 7','Year 8','Year 9']
            npv_df['Growth rates'] = rates
            amts = [int(i) for i in amts]
            npv_values = [int(i) for i in npv_values]
            npv_df['Projected cashflow'] = amts
            npv_df['PV of cashflows'] = npv_values
            npv_df.index = npv_df['Year']
            npv_df.pop('Year')
            npv_df = npv_df.applymap(str)
            with st.expander('Calculation'):
                st.markdown('Year 0 cashflow (Last year) =  &nbsp;'+ str(int(amt)) + ' mil')
                st.dataframe(npv_df.T, width=1000)
                st.markdown('Total PV of all future Cashflows =  &nbsp;'+ str(int(npv))+ ' mil')
                st.markdown('Terminal value using rate '+str(ter_rate)+'% =  &nbsp;'+str(int(terminal_value))+ ' mil')
                st.markdown('PV of Terminal value  =  &nbsp;'+str(int(pv_terminal_value))+ ' mil')
                st.markdown('Subtract Net Debt =  &nbsp;'+str(int(net_debt))+ ' mil')
                st.markdown('Net PV of the company = &nbsp; **' +str(int(dcf_value))+ '** mil')
            
            st.write("Current MCap: &nbsp; **"+str(int(quote['MarketCapitalization']))+' million**')
            
            margin_of_safety = int(((dcf_value/quote['MarketCapitalization'])-1)*100)
            if margin_of_safety <= 0:
                st.write(f'<b style="color:#d6616b">{"Margin of Safety: &nbsp; **"+str(margin_of_safety)+"%**"}</b>', unsafe_allow_html=True)
            else:
                st.write(f'<b style="color:#74c476">{"Margin of Safety: &nbsp;"+str(margin_of_safety)+"%"}</b>', unsafe_allow_html=True)
            #st.write("Margin of Safety : "+str(margin_of_safety)+"%")
        else:
            st.warning("Sorry, DCF Calculation doesn't work on loss making companies.")
landing_page()