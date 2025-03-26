import neo4j
import streamlit as st
import pandas as pd

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
# 案件搜索逻辑
# ============================
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


st.title("案件搜索系统 🕵️‍♂️")

# 搜索输入框
keyword = st.text_input("请输入关键词进行搜索：", "")

# 搜索按钮
if st.button("搜索"):
    if keyword.strip():
        try:
            # 调用搜索函数
            total_count, results = search_cases(keyword)

            # 显示搜索结果
            st.markdown(f"### 共找到 **{total_count}** 条匹配的案件：")

            if total_count > 0:
                for index, row in results.iterrows():
                    with st.expander(f"案件名称: **{row['name']}**", expanded=False):
                        st.markdown(f"**描述**: {row['description']}")
                        st.markdown(f"**类型**: {row['type']} - {row['subtype']}")
                        st.markdown(f"**嫌疑人**: {', '.join(row['suspects'])}")
                        st.markdown(f"**被害人**: {', '.join(row['victims'])}")
                        st.write("---")
            else:
                st.info("没有找到匹配的案件。")
        except Exception as e:
            st.error(f"搜索时发生错误: {e}")
    else:
        st.warning("请输入有效的关键词进行搜索。")