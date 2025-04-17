import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd

from collections import Counter
import json
from openai import OpenAI
import openai

with st.sidebar:

    with st.expander("📌 操作说明", expanded=True):
        st.markdown(
            """
        1. 📝 在文本框中输入待检测内容
        2. 🚀 点击「开始检测」按钮
        3. 📊 查看下方分析结果
        4. 🔍 使用下方工具进行深度分析
        """
        )

    with st.expander("⚙️ 高级选项"):
        confidence_threshold = st.slider(
            "置信度阈值", min_value=0.7, max_value=0.99, value=0.9, step=0.01
        )

        analysis_depth = st.selectbox("分析深度", ["快速模式", "标准模式", "深度模式"])
    
        st.header("DeepSeek API Key 配置")
        use_custom_openai = st.checkbox('自定义 DeepSeek 连接配置')
        
        if use_custom_openai:
            st.session_state.openai_api_key = st.text_input('OpenAI API Key', type='password')
            st.session_state.openai_model = st.text_input('OpenAI Model')
            st.session_state.openai_base_url = st.text_input('OpenAI Base URL')
        else:
            st.session_state.openai_api_key = st.secrets['OPENAI_API_KEY']
            st.session_state.openai_model = st.secrets['OPENAI_MODEL']
            st.session_state.openai_base_url = st.secrets['OPENAI_BASE_URL']
        
        if st.button('检查 API Key 可用性'):
            import openai
            with st.spinner('正在验证...'):
                try:
                    openai.base_url = st.session_state.openai_base_url
                    openai.api_key = st.session_state.openai_api_key
                    openai.models.retrieve(st.session_state.openai_model)
                    st.success('API Key 验证成功', icon='✅')
                except Exception as e:
                    st.error(e, icon='❌')
                    
@st.cache_resource(show_spinner=False)
def init_keywords():    
    with open("recognize/fraud_keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)
    return keywords

@st.cache_resource(show_spinner=False)
def init_msg_cls():
    from recognize import fraud_msg_cls
    return fraud_msg_cls.MsgClsModel()

with st.spinner("正在加载模型..."):
    keywords = init_keywords()
    keywords = [keywords[i][0] for i in range(len(keywords))]
    model = init_msg_cls()
    import jieba

# ---------------------------
# 页面配置
# ---------------------------
# st.set_page_config(
#     page_title="智能诈骗信息检测系统",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

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
        predictions = model.predict(text)
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
    
    /* 主标题 */
    .main-title {
        color: #E57373;
        font-size: 2.5em;
        text-align: center;
        padding: 20px;
        border-bottom: 3px solid #E57373;
        animation: titleAnimation 0.5s ease-out;
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

def get_suggestions_stream(msg, prediction):
    prompt_template = """
    我这里有一条疑似欺诈的信息，以下是信息内容：
    {msg}

    由我训练的模型得到，该短信属于的类别为：
    {prediction}

    请你根据我训练的模型的预测结果，针对模型预测的可能性最大的的**一种类别**，给出针对收到短信的风险用户建议。

    要求：
    1. 不要输出模型预测的概率值
    2. 可以针对短信中的内容的部分特征，结合模型预测的类别的典型特征，给出风险用户的建议。
    3. 如果模型预测的类别的典型特征不足以给出建议，可以根据短信的内容给出建议。
    4. 如果模型预测为无风险，可以恭喜用户，但也可以给出一些建议。
    5. 只需要给出约 200 字的建议即可。建议有条理地列出。
    6. 适量加入 emoji 表情，使得建议更加生动有趣。

    建议内容：
    """
    prompt = prompt_template.format(msg=msg, prediction=prediction)
    response_stream = OpenAI().chat.completions.create(
        model=st.session_state.openai_model,
        messages=[
            {"role": "system", "content": "The following is a message that I received from a user and I need your help to respond to it."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        temperature=1.0,
        stream=True,
    )
    return response_stream

# 开始检测

def visualize_result(input_text, result_container):
    # 检测输入文本长度
    with result_container:
        if len(input_text) < 10:
            st.error("⚠️ 输入文本过短，请至少输入10个字符")
        else:
        # 动态可视化组件
        # 运行
            with st.spinner("▸▸ 正在生成可视化报告..."):
                try:
                    result = predict_text(input_text)
                    st.toast(":rainbow[识别完成！]", icon="🥳")

                except Exception as e:
                    st.error(f"⚠️ 发生错误: {str(e)}")
                    st.stop()
                    
                # 可视化结果
                colored_header(
                    label="🎯 识别结果",
                    description="基于 **华为 NEZHA 模型** 微调的文本分类引擎 🚀",
                    color_name="gray-70",
                )
                    
                col1, col2, col3 = st.columns([1,1,1], gap="large")
                
                with col1:
                    # 获取并显示结果
                    st.toast(":rainbow[结果已就绪！]", icon="🎉")
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
                    # with result_container.container():
                    st.markdown(
                        f"""
                        <div style="padding:1rem; border-radius:15px; background:{color_map[risk_level]};">
                            <h3 style="color:white; text-align:center; margin:1rem 0;">{risk_level}</h2>
                            <h4 style="color:white; text-align:center; ">🎯 {result['prediction']}</h4>
                            <h5 style="color:white; text-align:left; ">⚠️ 危险关键词：{keywords_display}</h4>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    # st.markdown("### 📊 实时特征分析")
                    # 动态获取特征数据
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
                        title=dict(
                            text="风险特征雷达图",
                            x=0.38,
                            y=0.95,
                            font=dict(
                                size=14,
                            )
                        ),
                        polar=dict(
                            domain=dict(x=[0.1, 0.9], y=[0.1, 0.7]),
                            radialaxis=dict(range=[0, 100]),
                        ),
                        margin=dict(l=20, r=20, t=15, b=20),
                        height=250,
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                with col3:
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
                
            # 结果分析
            colored_header(
                label="💡 建议与防护",
                description="🔍 基于 **DeepSeek 大模型**的建议生成",
                color_name="gray-70",
            )
            
            with st.spinner("▸▸ 正在生成建议..."):
                try:
                    suggestions_stream = get_suggestions_stream(input_text, result['features']['风险等级'])
                    with st.expander("DeepSeek 建议", expanded=True, icon='🚀'):
                        st.write_stream(suggestions_stream)
                    st.toast(":rainbow[建议已生成！]", icon="🎉")
                except Exception as e:
                    st.error(f"⚠️ 发生错误: {str(e)}")
                    st.stop()
                
                
# ---------------------------
# 界面布局
# ---------------------------
# 标题
st.markdown('<h1 class="main-title">🛡️ 智能诈骗信息检测 🚀</h1>', unsafe_allow_html=True)
st.session_state.show_result = False

text_col, button_col = st.columns([3, 1], gap="large")
result_area = st.empty()



# 输入区域
with text_col:
    input_text = st.text_area(
        "📝 请输入待检测的文本内容：",
        height=100,
        placeholder="例：【顺丰】尊敬的客户，您使用顺丰的频率较高，现赠送您暖风扇一台，请添加支付宝好友进行登记领取。",
        help="支持中文文本检测，建议输入50-500字",
    )
with button_col:
    if st.button("开始检测", use_container_width=True, type="primary", help="点击进行诈骗信息检测"):
        visualize_result(input_text, result_area.container())
        st.session_state.show_result = True
    state_show = st.empty()
    if not st.session_state.get("show_result", False):
        state_show.info("请先输入待检测文本，然后点击「开始检测」按钮。", icon="ℹ️")
    else:
        state_show.success("检测完成！请查看下方结果。", icon="✅")
        st.balloons()


@st.cache_resource(show_spinner=False)
def draw_frq_fig():
    try:
        with open("recognize/fraud_keywords.json", "r", encoding="utf-8") as f:
            words = json.load(f)

            # 将词频数据转换为 DataFrame
            word_freq_df = pd.DataFrame(words, columns=["Word", "Frequency"])

            # 使用 plotly 生成更美观的直方图
            fig = px.bar(
                word_freq_df,
                x="Word",
                y="Frequency",
                text="Frequency",
                color="Frequency",
                color_continuous_scale="Viridis",
                labels={"Word": "关键词", "Frequency": "频率"}
            )

            # 设置图表样式
            fig.update_traces(
                texttemplate='%{text:.2s}', 
                textposition='outside',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5
            )
            return fig
            st.plotly_chart(fig, use_container_width=True)
    except FileNotFoundError:
        st.warning("词频文件未找到")
    except Exception as e:
        st.error(f"直方图加载失败: {str(e)}")

if not st.session_state.get("show_result", False):
    with result_area.container():
        col1, col2 = st.columns([1, 1], gap="large")
        with col1: # 词云图
            colored_header(
                label="🔍 风险关键词云图",
                description="✨ 基于诈骗信息数据库的关键词提取生成词云图",
                color_name="gray-70",
            )
            try:
                with open("recognize/wordcloud.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=800)
            except FileNotFoundError:
                st.warning("词云文件未找到")
            except Exception as e:
                st.error(f"词云加载失败: {str(e)}")
                
        with col2: # 词频直方图
            colored_header(
                label="📊 风险关键词直方图 ",
                description="🔑 基于诈骗信息数据库的关键词提取",
                color_name="gray-70",
            )
            fig = draw_frq_fig()
            st.plotly_chart(fig, use_container_width=True)
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
