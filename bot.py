import streamlit as st
from utils import write_message

# 示例问题列表
EXAMPLE_QUESTIONS = [
    "使用手机诈骗的案例有哪些？",
    "有哪些人涉及到了虚假投资？",
    "使用各类工具的诈骗案例分别占比多少？",
    "涉嫌团伙作案的案件有哪些？"
]

# Page Config
with st.sidebar:
    with st.expander("配置 OpenAI API Key"):
        use_custom_openai = st.checkbox('自定义 OpenAI 连接配置')
        
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
    if st.button('重置会话', icon='🔄'):
        st.session_state.messages = [
            {"role": "assistant", "content": "你好，我是关于反诈知识的问答助手。有什么可以帮助到你？🥰"},
        ]
        st.success('会话已重置', icon='✅')

if not st.session_state.logged_in:
    # 不允许用户使用
    st.error("请先登录")
    st.stop()



# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好，我是关于反诈知识的问答助手。有什么可以帮助到你？🥰"},
    ]

# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('Thinking...'):
        from agent import generate_response
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)

# 在聊天界面顶部添加示例问题按钮
st.write("试试这些常见问题：")
cols = st.columns(2)  # 创建两列来排列按钮
asked_example = None  # 用于存储用户选择的示例问题
for i, question in enumerate(EXAMPLE_QUESTIONS):
    with cols[i % 2]:  # 交替分配到两列
        if st.button(question, key=f"example_{i}"):
            # 直接处理问题提交
            # write_message('user', question)
            # handle_submit(question)
            asked_example = question

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle user input
if question := st.chat_input("键入新问题……") or asked_example:
    # Reset the asked_example variable
    question = question if question else asked_example
    asked_example = None
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
