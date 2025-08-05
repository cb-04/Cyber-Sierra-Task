import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from io import BytesIO
import os
from dotenv import load_dotenv

# --- Initialize Session State ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}



# --- Load Environment ---
load_dotenv()
user_key = os.getenv("MY_OPENAI_KEY")

# --- UI Setup ---
st.set_page_config(page_title="AI CSV Assistant", layout="wide")
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("AI-Powered CSV/Excel Assistant")
with col2:
    st.markdown("""<div style="text-align: right; color: #aaa; font-size: 0.9em;">Upload • Analyze • Visualize</div>""", 
                unsafe_allow_html=True)

# --- File Upload ---
with st.container():
    st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "**Upload your CSV/XLS/XLSX files**",
        accept_multiple_files=True,
        type=["csv", "xls", "xlsx"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- Process Uploaded Files ---
for uploaded_file in uploaded_files:
    try:
        filename = uploaded_file.name
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, sheet_name=None)
        st.session_state.dataframes[filename] = df
        st.toast(f"Loaded: {filename}")
    except Exception as e:
        st.error(f"Failed to load {uploaded_file.name}: {str(e)}")

# --- Main Analysis Section ---
if st.session_state.dataframes:
    # File selection
    with st.container():
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        file_choice = st.selectbox("Choose a file", list(st.session_state.dataframes.keys()))
        selected_file = st.session_state.dataframes[file_choice]
        
        if isinstance(selected_file, dict):
            sheet_choice = st.selectbox("Select worksheet", list(selected_file.keys()))
            df_to_show = selected_file[sheet_choice]
        else:
            df_to_show = selected_file
        st.markdown('</div>', unsafe_allow_html=True)

    # Data preview tabs
    tab1, tab2 = st.tabs(["Data Preview", "Data Summary"])
    with tab1:
        N = st.slider("Rows to display", 1, 100, 5)
        st.dataframe(df_to_show.head(N), use_container_width=True)
    with tab2:
        st.write("**Columns:**")
        st.code(list(df_to_show.columns))
        st.write("**Summary:**")
        st.dataframe(df_to_show.describe())

    # Analysis with history tracking
    with st.container():
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.subheader("Ask About Your Data")
        
        question = st.text_input("Enter your question", label_visibility="collapsed")
        
        if st.button("Analyze", type="primary", use_container_width=True) and question:
            with st.spinner("Analyzing..."):
                try:
                    # Prepare dataframe
                    df_for_agent = df_to_show.copy()
                    df_for_agent.columns = df_for_agent.columns.astype(str)
                    
                    # Configure PandasAI
                    llm = OpenAI(api_token=user_key)
                    config = {
                        "llm": llm,
                        "save_charts": False,
                        "save_charts_path": "/dev/null",
                        "enable_cache": False,
                        "verbose": False
                    }
                    pandas_ai = SmartDataframe(df_for_agent, config=config)
                    
                    # Get answer
                    answer = pandas_ai.chat(question)
                    
                    # Process answer
                    st.markdown("### Analysis Results")
                    if hasattr(answer, 'figure'):
                        buf = BytesIO()
                        answer.figure.savefig(buf, format='png', facecolor='#1e1e1e')
                        buf.seek(0)
                        st.image(buf, use_column_width=True)
                        plt.close(answer.figure)
                        answer_output = "Chart displayed above"
                    elif isinstance(answer, (pd.DataFrame, pd.Series)):
                        st.dataframe(answer)
                        answer_output = "Dataframe displayed above"
                    else:
                        st.write(answer)
                        answer_output = str(answer)
                    
                    # Store in history
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer_output,
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.success("Analysis complete")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- Chat History Section ---
    with st.expander("", expanded=True):
        if not st.session_state.chat_history:
            st.info("No history yet. Ask questions to build history.")
        else:
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container(border=True):
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"**Q:** {chat['question']}")
                        st.markdown(f"**A:** {chat['answer']}")
                    with col2:
                        st.caption(chat['timestamp'])
                        if st.button("↻", key=f"reuse_{i}"):
                            st.session_state.current_question = chat['question']

# --- Empty State ---
else:
    st.markdown("""<div class="empty-state"><h3>No files uploaded yet</h3></div>""", 
                unsafe_allow_html=True)