import streamlit as st
from utils import write_message

# Page Config
# st.set_page_config("Arcaea QA Bot", page_icon="😋")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好，我是 《韵律源点 (Arcaea)》 问答助手。有什么可以帮助到你？🥰"},
    ]

# Submit handler
def handle_submit(message):
    from agent import generate_response
    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if question := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
