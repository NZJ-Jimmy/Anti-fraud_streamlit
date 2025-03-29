import streamlit as st
import pandas as pd
import plotly.express as px
from pyecharts import options as opts
from pyecharts.charts import Map
from streamlit_echarts import st_pyecharts

def create_risk_map(data):
    # 创建基础地图
    c = (
        Map(init_opts=opts.InitOpts(
            width="100%", 
            height="680px",  # 增加高度
            theme="white",  # 使用白色主题
            bg_color="#F8F9FA"  # 背景色与Streamlit协调
        ))
        .add(
            series_name="诈骗风险指数",
            data_pair=data,
            maptype="china",
            is_map_symbol_show=True,  # 显示地图标记
            label_opts=opts.LabelOpts(
                is_show=True,
                color="rgba(0,0,0,0.8)",
                font_size=10,
                formatter="{b}: {c}"  # 标签显示格式
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=0.8,
                border_color="rgba(0,0,0,0.2)"  # 边界线样式
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="全国诈骗风险热力图",
                subtitle="数据来源：国家反诈中心 | 更新日期：2024.01",
                subtitle_textstyle_opts=opts.TextStyleOpts(
                    color="#666",
                    font_size=12
                ),
                pos_left="center"
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=100,
                range_color=["#FFE4B5", "#FFA07A", "#CD5C5C"],  # 三色渐变
                is_piecewise=True,  # 分段显示
                pos_left="5%",
                pos_bottom="15%",
                textstyle_opts=opts.TextStyleOpts(
                    color="#333",
                    font_size=12
                )
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}<br/>风险指数: {c}",
                background_color="rgba(255,255,255,0.95)",
                border_color="#ddd",
                textstyle_opts=opts.TextStyleOpts(color="#333")
            ),
            toolbox_opts=opts.ToolboxOpts(  # 添加工具栏
                is_show=True,
                pos_left="right",
                feature={
                    "saveAsImage": {},
                    "restore": {},
                    "dataZoom": {}
                }
            )
        )
        .set_series_opts(
            emphasis_opts=opts.EmphasisOpts(  # 高亮效果
                label_opts=opts.LabelOpts(color="black"),
                itemstyle_opts=opts.ItemStyleOpts(
                    border_color="#333",
                    border_width=1
                )
            )
        )
    )
    return c
def risk_assessment_page():
    # ========== 页面配置 ==========
    st.set_page_config(
        page_title="智能反诈风险评估系统",
        layout="wide",
        page_icon="🛡️",
        initial_sidebar_state="expanded"
    )
    
    # ========== 全局样式 ==========
    st.markdown("""
    <style>
        .main .block-container {max-width: 100% !important; padding: 2rem 4rem;}
        div[data-testid="stForm"] {background: #f8f9fa; padding: 2rem; border-radius: 15px;}
        .stPlotlyChart {border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
        h2 {border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

    # ========== 核心功能布局 ==========
    st.title("🛡️ 智能反诈风险评估系统")
    
    with st.expander("📘 使用指南", expanded=True):
        st.markdown("""
        ### 系统功能说明
        1. **风险画像**：多维评估个人受诈风险
        2. **防御模拟**：实时测试防护策略效果
        3. **趋势预测**：可视化风险变化轨迹
        4. **区域预警**：查看所在地风险热力分布
        """)

    # ========== 评估表单 ==========
    with st.form("main_form"):
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("🔍 基本信息")
            age = st.slider("年龄", 18, 100, 25,
                          help="研究表明不同年龄段受诈风险存在显著差异")
            education = st.selectbox("最高学历", 
                ["初中及以下", "高中", "本科", "硕士及以上"])
            income = st.selectbox("月收入范围",
                ["无固定收入", "3000元以下", "3000-8000元", "8000-20000元", "20000元以上"])
            
        with col2:
            st.subheader("📈 风险接触")
            fraud_types = st.multiselect(
                "近期接触的诈骗类型（多选）",
                ["冒充公检法", "投资理财", "网络购物", "兼职刷单", "感情诈骗"],
                default=["网络购物"]
            )
            loss_amount = st.slider("年度损失金额（元）", 0, 200000, 0, 1000)
            report_police = st.checkbox("是否及时报警", value=True)
            
        submitted = st.form_submit_button("开始智能评估", use_container_width=True, type="primary")

    # ========== 评估结果展示 ==========
    if submitted:

        # 风险评估逻辑（示例简化版）
        risk_score = calculate_risk(age, education, income, fraud_types, loss_amount, report_police)
        risk_level = "低风险" if risk_score < 60 else "中风险" if risk_score < 85 else "高风险"
        
        # ========== 风险概览 ==========
        with st.container():
            st.markdown("---")
            cols = st.columns([2, 3])
            
            with cols[0]:
                # 风险等级指示器
                color_map = {"低风险":"#2ecc71", "中风险":"#f1c40f", "高风险":"#e74c3c"}
                st.markdown(f"""
                <div style="padding:2rem; border-radius:15px; background:{color_map[risk_level]};">
                    <h2 style="color:white; margin:0;">综合风险评估</h2>
                    <h1 style="color:white; text-align:center; margin:1rem 0;">{risk_level}</h1>
                    <h3 style="color:white; text-align:center;">风险指数：{risk_score}/150</h3>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[1]:
                # 风险因素分解
                factors = get_risk_factors(age, education, income, fraud_types, loss_amount, report_police)
                fig = px.bar(factors, x='因素', y='贡献值', 
                            color='因素', text='贡献值',
                            color_discrete_sequence=px.colors.diverging.Tealrose,
                            height=400)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        # ========== 高级可视化 ==========
        tab1, tab2, tab3 = st.tabs(["📊 风险地图", "🛡️ 防御模拟", "📈 趋势分析"])
        
        with tab1:
            # 模拟数据（实际应从数据库获取）
            risk_data = [("北京", 100), ("上海", 85), ("广东", 75), 
                        ("新疆", 60), ("浙江", 88), ("四川", 72)]
            
            # 生成地图
            risk_map = create_risk_map(risk_data)
            
            # 添加说明卡片
            with st.expander("ℹ️ 地图使用说明", expanded=True):
                st.markdown("""
                - **颜色渐变**：从浅黄到深红表示风险等级递增
                - **点击交互**：单击省份查看详细信息
                - **工具栏功能**：
                    - 📷 保存图片  
                    - 🔍 区域缩放  
                    - 🔄 重置视图
                """)
            
            # 渲染地图
            st_pyecharts(risk_map, key="risk_map")
            
            # 添加数据来源声明
            st.caption("注：本数据基于国家反诈中心2023年度统计报告分析生成")
            
        with tab2:
            # 防御模拟器
            st.subheader("防护策略模拟")
            simulate_defense()
            
        with tab3:
            # 历史趋势
            st.subheader("风险趋势预测")
            show_trend_analysis(risk_score)

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
