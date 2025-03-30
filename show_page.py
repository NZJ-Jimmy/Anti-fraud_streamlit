import streamlit as st
import json
import os
from datetime import datetime
from filelock import FileLock
import uuid
import pandas as pd
import plotly.express as px

# 配置文件路径
DATA_FILE = "articles.json"
LOCK_FILE = DATA_FILE + ".lock"


# 初始化数据文件
@st.cache_data
def init_data():
    if not os.path.exists(DATA_FILE):
        with FileLock(LOCK_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"articles": []}, f, ensure_ascii=False, indent=4)


# 加载数据（原子操作）
@st.cache_data
def load_data():
    with FileLock(LOCK_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


# 保存数据（原子操作）
@st.cache_data
def save_data(data):
    with FileLock(LOCK_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 文章发布表单
def publish_article():
    with st.form("发表文章", clear_on_submit=True):
        title = st.text_input("文章标题", max_chars=50, help="最多50个字符")
        content = st.text_area("文章内容", height=200)
        author = st.text_input("作者", value="匿名")
        is_top = st.checkbox("置顶文章")
        submitted = st.form_submit_button("立即发布")

        if submitted:
            if not title or not content:
                st.error("标题和内容不能为空！")
            else:
                data = load_data()
                new_article = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "content": content,
                    "author": author,
                    "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "view_timestamps": [],  # 改为记录时间戳列表
                    "is_top": is_top,
                }
                data["articles"].append(new_article)
                save_data(data)
                st.success(f"✅文章发布成功！")


# 文章展示组件
def display_article(article, idx, is_hot=False):
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        if is_hot:
            rank_icons = ['🥇', '🥈', '🥉']
            icon = rank_icons[idx] if idx < 3 else ''
            title = f"{icon} {article['title']}"
        else:
            title = article['title']

        st.subheader(title)
        st.caption(f"作者：{article['author']} | 发布时间：{article['publish_time']}")
        # 更新热度值计算方式
        views_count = len(article["view_timestamps"])
        st.progress(views_count / 100 if views_count < 100 else 1.0, 
                text=f"热度值：{views_count}")

    # st.button
    with col2:
        button_key = f"read_{idx}_{article['id']}"
        if st.button("阅读全文", key=button_key):
            st.session_state.selected_article = article["id"]

    # 显示内容摘要
    content = article["content"]
    preview = (content[:20] + "...") if len(content) > 20 else content
    st.write(preview)
    st.divider()


# 文章详情页
def show_article_detail(article_id):
    data = load_data()
    article = next((a for a in data["articles"] if a["id"] == article_id), None)

    if not article:
        st.error("文章不存在")
        st.session_state.pop("selected_article", None)
        return

    # 更新阅读量
    article["view_timestamps"].append(datetime.now().isoformat())
    save_data(data)

    # 显示详情
    st.button("← 返回列表", key="back_btn", on_click=lambda: st.session_state.pop("selected_article"))
    st.title(article["title"])
    st.markdown(f"**作者**：{article['author']} ｜ **发布时间**：{article['publish_time']}")

    # 文章内容显示
    st.markdown("---")
    st.write(article["content"])
    st.markdown(f"<div style='text-align: right; color: #666;'>总阅读量：{len(article['view_timestamps'])}</div>", 
               unsafe_allow_html=True)

    # ========== 阅读趋势图（分钟级） ==========
    st.markdown("---")
    st.subheader("📈 阅读趋势")

    if len(article["view_timestamps"]) > 0:
        # 准备数据
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(article["view_timestamps"])
        })

        # 按分钟对齐时间戳（向下取整到整分钟）
        df["date"] = df["timestamp"].dt.floor('D')

        # 按分钟统计
        daily_views = df.groupby("date").size().reset_index(name="阅读量")

        # 创建可视化图表
        fig = px.line(
            daily_views,
            x="date",
            y="阅读量",
            markers=True,
            line_shape="spline",
            template="plotly_white",
            color_discrete_sequence=["#00CC96"],  # 使用更醒目的颜色
            labels={"date": "日期", "阅读量": "当日阅读量"},
        )

        # 美化图表样式
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showline=True,
                linecolor="lightgray",
                title="时间",
                type="date",  # 确保时间轴正确识别
                tickformat="%y-%m-%d",  # 显示月-日格式
                tickmode="auto",
                nticks=min(14, len(daily_views)),  # 最多显示14个日期刻度
                tickangle=30,  # 调整角度
            ),
            yaxis=dict(
                showline=True,
                linecolor="lightgray",
                title="阅读次数",
                rangemode="nonnegative",
            ),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=80),
            height=400,
        )

        # 添加峰值标记
        max_point = daily_views.loc[daily_views["阅读量"].idxmax()]
        fig.add_annotation(
            x=max_point['date'],
            y=max_point['阅读量'],
            text="峰值",
            showarrow=True,
            arrowhead=1
        )

        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无阅读数据")

# 主界面
def main():
    # st.set_page_config(page_title="个人文章管理", layout="wide")
    init_data()
    
    with st.sidebar:
        st.header("📝 文章管理")
        publish_article()
        st.markdown("---")
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()
    
    if "selected_article" in st.session_state:
        show_article_detail(st.session_state.selected_article)
    else:
        data = load_data()
        
        # 安全获取文章列表（核心修复）
        articles = data.get("articles", [])  # 添加默认值
        
        st.header("📰 最新文章")
        if not articles:
            st.info("还没有文章，快去发布一篇吧！")
        else:
            # 添加排序保护
            try:
                sorted_articles = sorted(
                    articles,
                    key=lambda x: (-int(x.get("is_top", False)), x.get("publish_time", "")),
                    reverse=True
                )[:10]
            except KeyError as e:
                st.error(f"数据格式错误：缺少字段 {e}")
                sorted_articles = articles[:10]
            
            for idx, article in enumerate(sorted_articles):
                display_article(article, idx)
        
        # st.markdown("---")
        st.header("🔥 热门文章")
        if articles:
            try:
                hot_articles = sorted(articles,  key=lambda x: len(x.get("view_timestamps", [])), reverse=True)[:3]
                for idx, article in enumerate(hot_articles):
                    display_article(article, idx, is_hot=True)  # 传入 is_hot 参数
            except KeyError:
                hot_articles = articles[:3]
                for idx, article in enumerate(hot_articles):
                    display_article(article, idx + 100)

main()
