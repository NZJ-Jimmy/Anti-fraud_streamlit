import streamlit as st
import pandas as pd
import plotly.express as px
from pyecharts import options as opts
from pyecharts.charts import Map
from streamlit_echarts import st_pyecharts
import plotly.graph_objects as go

def risk_assessment_page():
    # ========== 页面配置 ==========
    st.set_page_config(
        page_title="智能反诈风险评估系统",
        layout="wide",
        page_icon="🛡️",
        initial_sidebar_state="expanded"
    )

    # # ========== 全局样式 ==========
    # st.markdown("""
    # <style>
    #     .main .block-container {max-width: 100% !important; padding: 2rem 4rem;}
    #     div[data-testid="stForm"] {background: #f8f9fa; padding: 2rem; border-radius: 15px;}
    #     .stPlotlyChart {border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    #     h2 {border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem;}
    # </style>
    # """, unsafe_allow_html=True)

    # ========== 核心功能布局 ==========
    st.title("🛡️ 智能反诈风险评估")

    # ========== 核心功能布局 ==========
    with st.form("main_form"):
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            with st.expander("🔍 个人信息画像", expanded=True):
                age = st.slider(
                    "年龄",
                    18,
                    100,
                    25,
                    help="不同年龄段风险特征：\n- 青年(18-30)：网络诈骗高风险\n- 中年(31-50)：投资理财诈骗敏感\n- 老年(51+)：保健品诈骗易感",
                )
                residence = st.selectbox(
                    "常住地区",
                    ["城市", "县城", "农村"],
                    help="根据2023年反诈白皮书，农村地区金融诈骗报案率高出城市23%",
                )
                occupation = st.selectbox(
                    "职业类型",
                    ["学生", "在职员工", "自由职业", "退休人员", "其他"],
                    help="自由职业者遭遇兼职刷单诈骗的概率是其他职业的2.1倍",
                )
                income = st.selectbox("💴 月收入范围", ["无固定收入", "3000元以下", "3000-8000元", "8000-20000元", "20000元以上"])

            # 新增金融行为分析
            with st.expander("💳 金融行为分析", expanded=True):
                payment_methods = st.multiselect(
                    "常用支付方式（多选）",
                    ["刷脸支付", "微信支付", "银行卡支付", "动态令牌"],
                    default=["微信支付"],
                )
                investment_experience = st.selectbox(
                    "投资经验",
                    ["无", "1年以下", "1-3年", "3年以上"],
                    help="有投资经验的用户更易受到投资诈骗",
                )

        with col2:
            with st.expander("📈 风险接触分析", expanded=True):
                # 诈骗类型增加权重标识
                fraud_types = st.multiselect(
                    "近半年接触的诈骗类型（多选）",
                    [
                        ("冒充公检法"),
                        ("投资理财"),
                        ("网络购物"),
                        ("兼职刷单"),
                        ("感情诈骗"),
                        ("中奖诈骗"),
                        ("健康养生"),
                    ],
                    format_func=lambda x: x,
                    default=[("网络购物")],
                )

                loss_amount = st.slider("近一年被诈骗金额（元）", 0, 200000, 0, 1000)
                report_police = st.checkbox("是否及时报警", value=True)

            with st.expander("💡 心理评估", expanded=True):
                st.markdown("**遇到以下情况时您的反应：**")
                col_a, col_b, col_c = st.columns([1, 1, 1], gap="medium")

                with col_a:
                    urgency_react = st.radio(
                        "🕒 收到'紧急'通知时",
                        ("立即查看", "先核实再处理", "直接忽略"),
                        index=1,
                        help="研究表明80%的诈骗利用紧急心理"
                    )

                with col_b:
                    stranger_request = st.radio(
                        "👤 陌生人请求个人信息",
                        ("婉言拒绝", "视情况而定", "爽快提供"),
                        index=0,
                        help="信息泄露是诈骗的主要源头"
                    )

                with col_c:
                    reward_react = st.radio(
                        "🎁 面对未经验证的优惠信息",
                        ("果断举报", "保持怀疑", "积极参与"),
                        index=1,
                        help="高回报承诺通常是诈骗诱饵"
                    )
            social_media = st.slider("每日社交媒体使用时长(小时)", 
                                   0, 12, 3,
                                   help="过度暴露个人信息增加风险")

        submitted = st.form_submit_button(
            "开始风险评估", use_container_width=True, type="primary"
        )

    # ========== 评估结果可视化 ==========
    if submitted:
        user_profile = {
            "年龄": age,
            "地区": residence,
            "职业": occupation,
            "月收入范围": income,
            "支付方式": payment_methods,
            "投资经验": investment_experience,
            "接触诈骗类型": fraud_types,
            "近一年被诈骗金额": loss_amount,
            "是否报警": report_police,
            "紧急反应": urgency_react,
            "陌生人处理": stranger_request,
            "未验证优惠信息": reward_react,
            "每日社交使用时长": social_media,
        }
        # 创建结构化数据表
        # user_profile = pd.DataFrame(
        #     list(dicts.items()),
        #     columns=["属性", "值"],
        #     # "详细数据": [
        #     #     f"年龄：{age} | 地区：{residence} | 职业：{occupation} | 月收入范围：{income}",
        #     #     f"支付方式：{', '.join(payment_methods)} | 投资经验：{investment_experience}",
        #     #     f"接触诈骗类型：{len(fraud_types)}种 | 年度损失：{loss_amount}元 | 是否报警：{report_police}",
        #     #     f"紧急反应：{urgency_react} | 陌生人处理：{stranger_request} | 未验证优惠信息: {reward_react}",
        #     #     f"每日社交使用时长（小时）：{social_media}"
        #     # ]
        # )

        st.success("✅ 评估完成！已为您生成风险分析报告🫡")

        print(user_profile["接触诈骗类型"])

        # ========== 高级可视化 ==========
        tab1, tab2, tab3 = st.tabs(["📝 风险分析报告", "🛡️ 防御模拟", "📈 趋势分析"])

        with tab1:
            st.write(user_profile)

        with tab2:
            # 防御模拟器
            st.subheader("防护策略模拟")
            simulate_defense()

        with tab3:
            # 历史趋势
            st.subheader("风险趋势预测")
            show_trend_analysis(150)

def calculate_risk(age, education, income, fraud_types, loss_amount, report_police):
    """示例风险评估逻辑"""
    # 实现具体的风险评估算法
    # return min(150, 
    #           age_factor(age) + 
    #           edu_factor(education) + 
    #           income_factor(income) + 
    #           contact_factor(fraud_types) + 
    #           loss_factor(loss_amount, report_police))
    return 150

def get_risk_factors(*args):
    """生成风险因素数据"""
    # 实现具体因素分析逻辑
    return pd.DataFrame({
        '因素': ['年龄特征', '教育程度', '收入水平', '接触频率', '历史损失'],
        '贡献值': [25, 30, 20, 35, 40]
    })

def load_geo_data():
    """加载地理数据"""
    # 示例数据
    return pd.DataFrame({
        '城市': ['北京','上海','广州','深圳','成都'],
        '经度': [116.40,121.47,113.26,114.05,104.06],
        '纬度': [39.90,31.23,23.12,22.55,30.67],
        '风险指数': [82,78,85,88,75]
    })

def simulate_defense():
    """防御策略模拟"""
    cols = st.columns(3)
    with cols[0]:
        firewall = st.slider("📱 反诈APP防护等级", 1, 5, 3)
    with cols[1]:
        education = st.select_slider("📖 反诈学习频率", 
                                   ["从不","每月","每周","每天"])
    with cols[2]:
        alert = st.radio("🚨 预警接收方式", ["短信","APP推送","电话提醒"])
    
    # 模拟风险降低计算
    reduction = firewall*15 + {"从不":0,"每月":10,"每周":25,"每天":40}[education]
    st.metric("预计风险降低幅度", f"{reduction}%", delta_color="inverse")

def show_trend_analysis(current_score):
    """趋势分析"""
    # 生成模拟数据
    timeline = pd.date_range(start="2023-01", periods=6, freq='M')
    history = [82, 75, 68, 65, 63, current_score]
    
    fig = px.line(x=timeline, y=history, markers=True,
                 labels={'x':'时间', 'y':'风险指数'},
                 color_discrete_sequence=["#FF6B6B"])
    st.plotly_chart(fig, use_container_width=True)

risk_assessment_page()
