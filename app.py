import streamlit as st

st.session_state.neo4j_uri = st.secrets['NEO4J_URI']
st.session_state.neo4j_username = st.secrets['NEO4J_USERNAME']
st.session_state.neo4j_database = st.secrets['NEO4J_DATABASE']
st.session_state.neo4j_password = st.secrets['NEO4J_PASSWORD']


show_page = st.Page('show_page.py', title='展示界面', icon='🎈')
search_page = st.Page('search_page.py', title='搜索界面', icon='🔍')
risk_page = st.Page('risk_page.py', title='风险界面', icon='⚠️')

pages = [show_page, search_page, risk_page]
pg = st.navigation(pages)
pg.run()
