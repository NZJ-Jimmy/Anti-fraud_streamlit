import streamlit as st
import pandas as pd
import neo4j
from pyvis.network import Network
import plotly.express as px
import time

# 彩虹色横线
rainbow_div = """
<div style="height: 5px; background: linear-gradient(90deg, 
    #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); 
    margin: 10px 0; border-radius: 2px;"></div>
"""


# ============================
# 数据库连接配置
# ============================
def connect_to_neo4j():
    """连接 Neo4j 数据库"""
    uri = st.session_state.neo4j_uri
    username = st.session_state.neo4j_username
    password = st.session_state.neo4j_password
    database = st.session_state.neo4j_database

    return neo4j.GraphDatabase.driver(uri, auth=(username, password), database=database)


# ============================
# 界面美化配置（添加在文件开头）
# ============================
# st.set_page_config(
#     page_title="智能反诈案件分析系统",
#     page_icon="🕵️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# 自定义CSS样式
st.markdown("""
<style>
    /* 主标题 */
    .main-title {
        color: #2E86C1;
        font-size: 2.5em;
        text-align: center;
        padding: 20px;
        border-bottom: 3px solid #2E86C1;
    }
    
    /* 搜索框美化 */
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 12px;
    }
    
    /* 卡片式布局 */
    .case-card {
        border: 1px solid #D6DBDF;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background: white;
    }
    
    /* 统计卡片 */
    .metric-box {
        background: #F8F9F9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-title">🔍 案件搜索</h1>', unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def search_cases(keyword, skip=0, limit=10):
    """
    根据关键词在 Neo4j 数据库中搜索案件。

    Args:
        keyword (str): 用于在案件内容、描述或名称中搜索的关键词。
        skip (int, 可选): 要跳过的记录数。默认为 0。
        limit (int, 可选): 要返回的最大记录数。默认为 10。

    Returns:
        tuple: 包含匹配案件总数、查询结果的 pandas DataFrame 的元组。
    """
    count_query_template = """
    MATCH (case:案件)
    WHERE case.content CONTAINS $keyword
        OR case.description CONTAINS $keyword
        OR case.name CONTAINS $keyword
    RETURN count(case) AS count
    """

    query_template = """
    MATCH (case:案件)-[:涉及嫌疑人]->(suspect)
    MATCH (case:案件)-[:涉及被害人]->(victim)
    MATCH (case:案件)-[:诈骗类型]->(fraud_type)
    WHERE case.content CONTAINS $keyword
        OR case.description CONTAINS $keyword
        OR case.name CONTAINS $keyword
    RETURN
        case.name AS name,
        case.description AS description,
        fraud_type.name AS type,
        fraud_type.subtype AS subtype,
        COLLECT(DISTINCT suspect.name) AS suspects,
        COLLECT(DISTINCT victim.name) AS victims
    SKIP $skip LIMIT $limit
    """

    driver = connect_to_neo4j()
    with driver.session() as session:
        # 查询案件总数
        count_result = session.run(count_query_template, keyword=keyword)
        total_count = count_result.single()["count"]

        # 查询案件详情
        result = session.run(query_template, keyword=keyword, skip=skip, limit=limit)
        return total_count, pd.DataFrame(result.data())


# 在搜索输入框下方添加筛选条件侧边栏
with st.sidebar:
    st.header("高级筛选")
    case_type = st.selectbox("案件类型", ["全部", "电信诈骗", "网络诈骗", "金融诈骗"])
    date_range = st.date_input("时间范围", [])
    risk_level = st.slider("风险等级", 1, 5, (1,5))

# 搜索输入框
keyword = st.text_input("请输入关键词进行搜索：", "")
# 搜索按钮
if st.button("开始搜索", key="search_btn", help="点击进行多维度案件分析", use_container_width=True, type='primary'):
    # 原有搜索逻辑
    if keyword.strip():
        try:
            # 调用搜索函数
            total_count, results = search_cases(keyword)

            # 显示搜索结果
            st.markdown(f"### 共找到 **{total_count}** 条匹配的案件：")
            if total_count > 0:
                st.toast(":rainbow[搜索完成！]", icon="🥳")
                for index, row in results.iterrows():
                    # st.subheader(f"案件名称：{row['name']}", divider="rainbow")

                    with st.expander(f"**案件详情**: **{row['name']}**", expanded=False):
                        st.markdown(f"####  案件名称: {row['name']}")
                        st.markdown(f"**描述**: {row['description']}")
                        st.markdown(f"**类型**: {row['type']} - {row['subtype']}")
                        st.markdown(f"**嫌疑人**: {', '.join(row['suspects'])}")
                        st.markdown(f"**被害人**: {', '.join(row['victims'])}")
                        # st.markdown(rainbow_div, unsafe_allow_html=True)
                        time.sleep(0.2)
            else:
                st.info("没有找到匹配的案件。")
                st.toast(":grey[没有找到匹配的案件。]", icon="😴")
        except Exception as e:
            st.error(f"搜索时发生错误: {e}")
    else:
        st.warning("请输入有效的关键词进行搜索。")
