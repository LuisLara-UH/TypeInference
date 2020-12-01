import streamlit as st
from TypeTools import run_pipeline

code = st.text_area('Codigo COOL:')
text = run_pipeline(code)
st.text(text)
