import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import time
import torch
import fraud_msg_cls
import jieba
from collections import Counter
import json

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

with open("fraud_keywords.json", "r", encoding="utf-8") as f:
    keywords = json.load(f)
keywords = [keywords[i][0] for i in range(len(keywords))]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------
# 页面配置
# ---------------------------
st.set_page_config(
    page_title="智能诈骗信息检测系统",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def extract_keywords(text, top_k=3):
    """提取文本中的危险关键词"""
    words = jieba.lcut(text)
    
    # 过滤条件：长度 > 1 + 非停用词 + 属于危险词表
    stopwords = {'的', '了', '是', '在', '和', '就', '都', '而', '及', '与', '这', '那', '有'}
    danger_words = [
        word for word in words 
        if len(word) > 1 
        and word not in stopwords 
        and word in keywords
    ]
    
    # 统计词频并排序
    word_counts = Counter(danger_words)
    
    # 获取排序后的关键词列表
    result = [word for word, _ in word_counts.most_common(top_k)]
    
    # 如果没有检测到关键词，返回包含"无"的列表
    return result if result else ["无"]


def get_risk_level(res, prob):
    """根据概率计算风险等级"""
    if res == "无风险":
        return "无风险"
    elif prob > 0.7:
        return "高风险"
    elif prob > 0.5:
        return "中风险"
    else:
        return "低风险"


def predict_text(text):
    try:
        predictions = fraud_msg_cls.predict(text)
        max_category, max_prob = predictions[0]

        # 特征计算函数
        def calculate_link_risk(text):
            """链接风险计算：检查文本中的URL"""
            import re

            url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[^\s]+"
            urls = re.findall(url_pattern, text)
            return min(len(urls) * 60 + 30, 100)  # 每个链接增加30%风险，上限100%

        def calculate_keyword_risk(text):
            """关键词风险：基于预定义诈骗词表"""
            words = jieba.lcut(text)
            hit_count = sum(1 for word in words if word in keywords)
            return min(hit_count * 20 + 28, 100)  # 每个关键词20%，上限100%

        def calculate_urgency_score(text):
            """紧迫性评分：检测时间敏感词汇"""
            urgency_words = ["立即", "马上", "尽快", "赶快", "今天", "现在", "机会"]
            words = jieba.lcut(text)
            count = sum(1 for word in words if word in urgency_words)
            return min(count * 25 + 32, 100)  # 每个词25%，上限100%

        return {
            "prediction": max_category,
            "probability": float(max_prob),
            "features": {
                "风险等级": get_risk_level(max_category, max_prob),
                "关键词": extract_keywords(text),
                # 实时特征
                "关键词风险": calculate_keyword_risk(text),
                "链接风险": calculate_link_risk(text),
                "紧迫性指数": calculate_urgency_score(text),
                "语义异常度": max_prob * 100,  # 直接使用模型置信度
            },
            "full_predictions": predictions,  # 保留完整预测结果
        }
    except Exception as e:
        st.error(f"分析失败: {str(e)}")
        return None

# ---------------------------
# 侧边栏说明
# ---------------------------
with st.sidebar:
    st.header("🔖 使用指南")
    with st.expander("📌 操作说明"):
        st.markdown(
            """
        1. 在文本框中输入待检测内容
        2. 点击「开始检测」按钮
        3. 查看下方分析结果
        4. 使用下方工具进行深度分析
        """
        )

    with st.expander("⚙️ 高级选项"):
        confidence_threshold = st.slider(
            "置信度阈值", min_value=0.7, max_value=0.99, value=0.85, step=0.01
        )

        analysis_depth = st.selectbox("分析深度", ["快速模式", "标准模式", "深度模式"])
    
    with st.container(border=True):
        st.markdown("### ☁️ 动态词云")
        try:
            with open("wordcloud.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=300)
        except FileNotFoundError:
            st.warning("词云文件未找到")
        except Exception as e:
            st.error(f"词云加载失败: {str(e)}")


# ---------------------------
# 自定义样式
# ---------------------------
st.markdown(
    """
<style>
    /* 主标题动画 */
    @keyframes titleAnimation {
        0% { transform: translateY(-20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    
    .main-title {
        animation: titleAnimation 1s ease-out;
        font-size: 2.8rem;
        text-align: center;
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem 0;
    }
    
    /* 输入框美化 */
    .stTextInput>div>div>input {
        border-radius: 15px;
        padding: 1.2rem;
        box-shadow: 0 2px 6px rgba(255,107,107,0.2);
    }
    
    /* 动态结果卡片 */
    .result-card {
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    /* 诈骗结果样式 */
    .fraud-result {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white;
    }
    
    /* 正常结果样式 */
    .normal-result {
        background: linear-gradient(135deg, #63cdda, #77ecb9);
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------
# 界面布局
# ---------------------------
colored_header(
    label="智能诈骗信息检测",
    description="基于 DeepSeek 微调的文本分类引擎",
    color_name="gray-70",
)

# 输入区域
with st.container(border=True):
    input_text = st.text_area(
        "📝 请输入待检测的文本内容：",
        height=100,
        placeholder="例：【顺丰】尊敬的客户，您使用顺丰的频率较高，现赠送您暖风扇一台，请添加支付宝好友进行登记领取。",
        help="支持中文文本检测，建议输入50-500字",
    )

# 动态可视化组件
col1, col2 = st.columns([5, 3])

# progress 状态精确控制进度百分比
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "new_result" not in st.session_state:
    st.session_state.new_result = False

with col1:
    # 使用独立容器控制结果显示
    result_container = st.empty()
    # 检测结果展示
    holder = st.empty()
    eval_bar = holder.progress(0.0, "**😴未开始检测**")
    if st.button("开始检测", use_container_width=True, type="primary"):
        if len(input_text) < 10:
            st.error("⚠️ 输入文本过短，请至少输入10个字符")
        else:
            # 重置状态
            st.session_state.new_result = False
            st.session_state.progress = 0

            eval_bar.progress(0.0, "**🤯分析中...**")
            try:
                # 获取并显示结果
                with st.spinner("▸▸ 正在生成可视化报告..."):
                    result = predict_text(input_text)
                    st.session_state["detection_result"] = result
                    # 立即清除旧结果
                    result_container.empty()

                # 模拟进度条（后执行）
                while st.session_state.progress < 100:
                    st.session_state.progress += 1
                    eval_bar.progress(st.session_state.progress, f"**🤯 深度分析中... {st.session_state.progress}%**")
                    time.sleep(0.03)

                st.session_state["new_result"] = True
                # 完成时显示
                eval_bar.progress(100, "**🫡 分析完成！**")
                time.sleep(0.5)
                st.toast(":rainbow[结果已就绪！]", icon="🎉")

            finally:
                st.toast(":rainbow[识别完成！]", icon="🥳")

    # 检测结果展示（确保即使没点按钮，仍可显示之前的结果）
    if "detection_result" in st.session_state and st.session_state["new_result"]:
        result = st.session_state["detection_result"]
        risk_level = result['features']['风险等级']
        keywords = result['features']['关键词']
        # 颜色映射配置
        color_map = {
            "无风险": "#2ecc71",
            "低风险": "#f1c40f",
            "中风险": "#f39c12",
            "高风险": "#e74c3c"
        }
        # 动态生成显示内容
        keywords_display = '无' if risk_level == "无风险" else ', '.join(keywords) or '无'
        with result_container.container():
            st.markdown(
                f"""
                <div style="padding:1rem; border-radius:15px; background:{color_map[risk_level]};">
                    <h2 style="color:white; text-align:center; margin:0;">📊 综合风险评估</h2>
                    <h2 style="color:white; text-align:center; margin:1rem 0;">{risk_level}</h2>
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                ### 🎯 检测结果：{result['prediction']}
                ### ⚠️ 危险关键词： {keywords_display}
                """
            )


with col2:
    st.markdown("### 📊 实时特征分析")
    with st.container(border=True):
        # 初始状态/未检测时的提示
        if "detection_result" not in st.session_state or not st.session_state["new_result"]:
            st.info("🕒 等待检测数据...")
        else:
            # 动态获取特征数据
            result = st.session_state["detection_result"]
            risk_level = result["features"]["风险等级"]

            # 根据风险等级调整语义指标
            raw_semantic_value = result["features"]["语义异常度"]  # 获取原始值
            semantic_label = "安全置信度" if risk_level == "无风险" else "语义异常度"

            features = {
                "关键词风险": result["features"]["关键词风险"],
                semantic_label: raw_semantic_value,  # 动态标签名
                "链接风险": result["features"]["链接风险"],
                "紧迫性指数": result["features"]["紧迫性指数"],
            }

            # 雷达图数据准备
            categories = list(features.keys())
            values = list(features.values())

            # 使雷达图闭合
            values += [values[0]]
            categories += [categories[0]]

            # 创建雷达图
            fig_radar = go.Figure()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill="toself",
                    marker=dict(size=8, color="#ff4b4b"),
                    line=dict(color="#ff4b4b", width=3),
                    name="特征评分",
                )
            )
            fig_radar.update_layout(
                polar=dict(
                    domain=dict(x=[0.1, 0.9], y=[0.1, 0.7]),
                    radialaxis=dict(range=[0, 100]),
                ),
                margin=dict(l=20, r=20, t=15, b=20),
                height=320
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # 创建仪表盘
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=result["probability"] * 100,
                    number={"suffix": "%"},
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "置信度仪表盘"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#ff6b6b"},
                        "steps": [
                            {"range": [0, 30], "color": "#63cdda"},
                            {"range": [30, 70], "color": "#ffeaa7"},
                            {"range": [70, 100], "color": "#ff6b6b"},
                        ],
                        "shape": "angular",
                    },
                )
            )
            fig_gauge.update_layout(
                height=200,
                margin=dict(t=50, b=8)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)


# ---------------------------
# 底部信息
# ---------------------------
st.markdown("---")
footer = """
<div style="text-align: center; padding: 1rem; color: #666;">
    <div style="margin-bottom: 0.5rem;">
        🛡️ 安全提示：本系统检测结果仅供参考，请勿直接作为处置依据
    </div>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
