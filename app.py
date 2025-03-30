import streamlit as st
# import start_page
# import bot

st.set_page_config(
    page_title="Anti-fraud QA",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.logo("./assets/logo.png", size='large')
                
                
start_page = st.Page("start_page.py", title="欢迎", icon="🎉")
bot_page = st.Page('bot.py', title='问答助手', icon='🤖')
search_page = st.Page('search.py', title='案件搜索', icon='🔍')
show_page = st.Page('show_page.py', title='展示界面', icon='🎈')
risk_page = st.Page('risk_page.py', title='风险界面', icon='⚠️')
recognize_page = st.Page('recognize_page.py', title='短信识别', icon='📩')

pages = [start_page, bot_page, search_page, show_page, risk_page, recognize_page]
pg = st.navigation(pages)
pg.run()
