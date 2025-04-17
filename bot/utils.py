import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

# tag::write_message[]
def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state


    # Write to UI
    with st.chat_message(role):
        if type(content) == str:
            result = content
        else:
            with st.spinner("正在生成内容……"):
                with st.expander("思考链", expanded=False):
                    result = st.write_stream(content)
                    result = result[-1]["output"]
        st.markdown(result)
        if save:
            st.session_state.messages.append({"role": role, "content": result})
# end::write_message[]

# tag::get_session_id[]
def get_session_id():
    return get_script_run_ctx().session_id
# end::get_session_id[]