import streamlit as st
import streamlit.components.v1 as components

col1, col2, col3 = st.columns([1,2.5,1])
with col2:
    st.image("https://media.giphy.com/media/AgHBbekqDik0g/giphy.gif", width = 400)
st.write('##')    

col1, col2, col3 = st.columns([0.5,4.5,0.5])
with col2:
    st.write("<h4 style='text-align: center;'>If you like my work and find value in it, please consider supporting. Your support will go a long way in allowing me to continue working on such projects. Thank You ❤️ </h4>", unsafe_allow_html=True)
    #st.markdown("If you like my work and find value in it, please consider supporting. Your support will go a long way in allowing me to continue working on such projects. Thank You ❤️")
# col1, col2, col3 = st.columns(3)
# with col2:
    
#     st.write(f'''
#         <div class="text-centerr">
#             <a target="_blank" href="https://buymeacoffee.com/stocksnapshot">
#                 <button>
#                     Buy me a Green Tea 🍵
#                 </button>
#             </a>
#         </div>
#         ''',
#         unsafe_allow_html=True
#     )
col1, col2, col3 = st.columns([1,1.5,1])
with col2: 
    components.html('''
        <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="stocksnapshot" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee?" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
    '''
        )
    #components.html('''
    #     <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script><script type='text/javascript'>kofiwidget2.init('Tip me a Coffee', '#29abe0', 'L3L6D661Q');kofiwidget2.draw();</script> ''')
# components.html(''''
# <div id="smart-button-container">
#       <div style="text-align: center;">
#         <div id="paypal-button-container"></div>
#       </div>
#     </div>
#   <script src="https://www.paypal.com/sdk/js?client-id=sb&enable-funding=venmo&currency=USD" data-sdk-integration-source="button-factory"></script>
#   <script>
#     function initPayPalButton() {
#       paypal.Buttons({
#         style: {
#           shape: 'rect',
#           color: 'gold',
#           layout: 'vertical',
#           label: 'paypal',
          
#         },

#         createOrder: function(data, actions) {
#           return actions.order.create({
#             purchase_units: [{"amount":{"currency_code":"USD","value":5}}]
#           });
#         },

#         onApprove: function(data, actions) {
#           return actions.order.capture().then(function(orderData) {
            
#             // Full available details
#             console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));

#             // Show a success message within this page, e.g.
#             const element = document.getElementById('paypal-button-container');
#             element.innerHTML = '';
#             element.innerHTML = '<h3>Thank you for your payment!</h3>';

#             // Or go to another URL:  actions.redirect('thank_you.html');
            
#           });
#         },

#         onError: function(err) {
#           console.log(err);
#         }
#       }).render('#paypal-button-container');
#     }
#     initPayPalButton();
#   </script>
#   ''')