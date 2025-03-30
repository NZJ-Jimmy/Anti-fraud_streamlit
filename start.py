import streamlit as st
from streamlit import session_state as ses


st.title(":rainbow[「智镜·无垠」]")
st.markdown("### :rainbow[*基于AI与知识图谱的全维度反诈中枢*]")
video_path = "logo.mp4"
st.video(video_path, autoplay=True, muted=True, loop=True)
