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
                                   0, 24, 3,
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
        # tab1, tab2, tab3 = st.tabs(["📝 风险分析报告", "🛡️ 防御模拟", "📈 趋势分析"])
        tab1, tab2 = st.tabs(["📝 风险分析报告", "📊 指标关联分析"])
        # "🛡️ 防御模拟", "📈 趋势分析",
        with tab1:
            st.write(user_profile)
        with tab2:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(
                    "<h3 style='text-align: center;'>风险因子关联分析热力图</h3>",
                    unsafe_allow_html=True,
                )

                # 数据预处理
                sample_data = pd.DataFrame({
                    "年龄": [28, 35, 22, 45, 31, 27, 50, 38, 29, 33],
                    "地区编码": [0, 0, 1, 2, 0, 1, 2, 0, 0, 1],
                    "收入等级": [3, 4, 2, 2, 3, 3, 1, 4, 2, 3],
                    "社交时长": [5, 3, 7, 2, 4, 6, 1, 3, 5, 4],
                    "诈骗类型数": [3, 1, 2, 0, 2, 4, 1, 2, 3, 1],
                    "心理评估分": [65, 82, 48, 73, 70, 55, 60, 85, 68, 58],
                    "风险值": [85, 68, 92, 58, 75, 88, 63, 70, 82, 78]
                })

                # 计算相关系数矩阵
                corr_matrix = sample_data.corr(method='spearman')

                # 生成热力图
                fig = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    color_continuous_scale='RdBu_r',
                    labels=dict(color="相关系数"),
                    width=650,
                    height=650
                )
                fig.update_layout(
                    xaxis=dict(tickangle=45, tickfont=dict(size=10)),
                    yaxis=dict(tickfont=dict(size=10)),
                )
                fig.update_traces(
                    hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>相关系数: %{z:.2f}",
                    hoverongaps=False
                )

                # 可视化呈现
                st.plotly_chart(fig, use_container_width=True)

                # 数据表格展示
                with st.expander("📜 原始相关系数矩阵"):
                    styled_matrix = corr_matrix.style\
                        .background_gradient(cmap='RdBu_r', vmin=-1, vmax=1)\
                        .format("{:.2f}")\
                        .set_table_styles([{
                            'selector': 'th',
                            'props': [('font-size', '10pt'), 
                                    ('background-color', '#f8f9fa')]
                        }])
                    st.dataframe(styled_matrix, use_container_width=True)

                # with c2:
                #     st.markdown(
                #         "<h3 style='text-align: center;'>多维度风险特征分析</h3>",
                #         unsafe_allow_html=True,
                #     )

                #     # 使用与热力图相同的数据集
                #     parallel_data = sample_data.copy()

                #     # 创建分类变量映射（增强可解释性）
                #     area_mapping = {0: "城市", 1: "县城", 2: "农村"}
                #     income_mapping = {
                #         1: "无固定收入",
                #         2: "3000以下",
                #         3: "3000-8000",
                #         4: "8000+",
                #     }

                #     parallel_data["地区类型"] = parallel_data["地区编码"].map(area_mapping)
                #     parallel_data["收入等级"] = parallel_data["收入等级"].map(
                #         income_mapping
                #     )

                #     # 生成平行坐标图
                #     fig = px.parallel_coordinates(
                #         parallel_data,
                #         color="风险值",
                #         dimensions=[
                #             "年龄",
                #             "地区类型",
                #             "收入等级",
                #             "社交时长",
                #             "诈骗类型数",
                #             "心理评估分",
                #             "风险值",
                #         ],
                #         color_continuous_scale=px.colors.diverging.Tealrose,
                #         labels={
                #             "年龄": "年龄（岁）",
                #             "社交时长": "日均社交时长（小时）",
                #             "诈骗类型数": "遭遇诈骗类型数",
                #             "心理评估分": "心理脆弱指数",
                #             "风险值": "风险评分",
                #         },
                #         height=700,
                #     )

                #     # 样式优化
                #     fig.update_layout(
                #         margin=dict(l=80, r=50, t=80, b=50),
                #         coloraxis_colorbar=dict(
                #             title="风险梯度",
                #             thicknessmode="pixels",
                #             thickness=20,
                #             lenmode="pixels",
                #             len=300,
                #             yanchor="middle",
                #             y=0.5,
                #         ),
                #         font=dict(size=10),
                #     )

                #     # 添加分析注释
                #     fig.add_annotation(
                #         x=0.95,
                #         y=1.15,
                #         xref="paper",
                #         yref="paper",
                #         text="▲ 线条颜色越暖代表风险越高",
                #         showarrow=False,
                #         font=dict(color="#666666"),
                #     )

                #     st.plotly_chart(fig, use_container_width=True)

                #     # 数据说明折叠面板
                #     with st.expander("📌 分析指南"):
                #         st.markdown(
                #             """
                #         ### 图形解读技巧：
                #         - **颜色映射**：暖色调（红）→ 高风险，冷色调（蓝）→ 低风险
                #         - **连线模式**：观察陡峭的转折点，识别异常关联路径
                #         - **特征聚类**：垂直线段聚集区域表示特征值集中分布
                #         - **典型路径**：鼠标悬停可追踪完整个体特征轮廓
                #         """
                #         )

                with c2:
                    st.markdown(
                        "<h3 style='text-align: center;'>多变量关联路径分析图</h3>",
                        unsafe_allow_html=True,
                    )

                    # 扩展数据
                    parallel_df = pd.DataFrame({
                        '年龄': [28, 35, 22, 45, 31, 27, 50, 38, 29, 33],
                        '收入等级': [3, 4, 2, 2, 3, 3, 1, 4, 2, 3],
                        '社交时长': [5, 3, 7, 2, 4, 6, 1, 3, 5, 4],
                        '诈骗类型数': [3, 1, 2, 0, 2, 4, 1, 2, 3, 1],
                        '心理评估分': [65, 82, 48, 73, 70, 55, 60, 85, 68, 58],
                        '风险值': [85, 68, 92, 58, 75, 88, 63, 70, 82, 78]
                    })

                    # 创建平行坐标图
                    fig = px.parallel_coordinates(
                        parallel_df,
                        color="风险值",
                        color_continuous_scale=px.colors.diverging.Tealrose,
                        labels={
                            "年龄": "Age",
                            "收入等级": "Income Level",
                            "社交时长": "Social Time",
                            "诈骗类型数": "Fraud Types",
                            "心理评估分": "Psychological Score",
                            "风险值": "Risk Value"
                        },
                        height=750,
                    )
                    fig.update_traces(line=dict(width=3))
                    # 调整图表边距，使布局更加紧凑
                    fig.update_layout(
                        margin=dict(l=80, r=50, t=80, b=50),
                        font=dict(size=13),
                        xaxis=dict(
                            tickangle=45,
                            tickfont=dict(size=10, color="black"),  # 设置刻度颜色为黑色
                        ),
                        yaxis=dict(
                            tickfont=dict(size=10, color="black")  # 设置刻度颜色为黑色
                        ),
                    )

                    # 显示平行坐标图
                    st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("请填写所有信息后点击开始风险评估查看结果😴")

risk_assessment_page()
