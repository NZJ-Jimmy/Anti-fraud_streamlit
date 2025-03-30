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


st.session_state.logged_in = False

with st.sidebar:
    with st.expander("连接 Neo4j 数据库"):
        use_custom_neo4j = st.checkbox('自定义 Neo4j 连接配置')

        if use_custom_neo4j:
            st.session_state.neo4j_uri = st.text_input('Neo4j URL')
            st.session_state.neo4j_username = st.text_input('Neo4j 用户名')
            st.session_state.neo4j_database = st.text_input('Neo4j 数据库')
            st.session_state.neo4j_password = st.text_input('Neo4j 密码', type='password')
        else:
            st.session_state.neo4j_uri = st.secrets['NEO4J_URI']
            st.session_state.neo4j_username = st.secrets['NEO4J_USERNAME']
            st.session_state.neo4j_database = st.secrets['NEO4J_DATABASE']
            st.session_state.neo4j_password = st.secrets['NEO4J_PASSWORD']

        if st.button('检查连接可用性'):
            from neo4j import GraphDatabase
            with st.spinner('正在连接...'):
                try:
                    with GraphDatabase.driver(
                        uri=st.session_state.neo4j_uri, 
                        auth=(st.session_state.neo4j_username, 
                            st.session_state.neo4j_password),
                        database=st.session_state.neo4j_database
                        ) as driver:
                            driver.verify_connectivity()
                            st.success('连接成功', icon='✅')
                except Exception as e:
                    st.error(e, icon='❌')

        
    with st.expander("用户登录"):
        # st.text_input('用户名')
        if st.text_input('验证码',type="password") == st.secrets['LOGIN_CODE']:
            st.session_state.logged_in = True
            st.success('登录成功', icon='✅')
                
                
start_page = st.Page("start_page.py", title="欢迎", icon="🎉")
bot_page = st.Page('bot.py', title='问答助手', icon='🤖')
search_page = st.Page('search.py', title='案件搜索', icon='🔍')
show_page = st.Page('show_page.py', title='展示界面', icon='🎈')
risk_page = st.Page('risk_page.py', title='风险界面', icon='⚠️')
recognize_page = st.Page('recognize_page.py', title='短信识别', icon='📩')

pages = [start_page, bot_page, search_page, show_page, risk_page, recognize_page]
pg = st.navigation(pages)
pg.run()
