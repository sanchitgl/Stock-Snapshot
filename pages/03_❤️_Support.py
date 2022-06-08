import streamlit as st


col1, col2, col3 = st.columns([1, 2.5, 1])
with col2:
    st.image("https://media.giphy.com/media/AgHBbekqDik0g/giphy.gif", use_column_width=True)
st.write('##')
st.write("<h3 style='text-align: center;'>If you like my work and find value in it, please consider supporting. Your support will go a long way in allowing me to continue what I love to do. Thank You ❤️ </h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col2:
    st.write(f'''
        <div class="text-centerr">
            <a target="_blank" href="https://buymeacoffee.com/stocksnapshot">
                <button>
                    Buy me a Green Tea 🍵
                </button>
            </a>
        </div>
        ''',
        unsafe_allow_html=True
    )



