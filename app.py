import os
import base64
import streamlit as st
from pickleball_agent import pickleball_agent  # the file above


st.set_page_config(
    page_title="Pickleball FAQ Bot",
    page_icon="🏓",
    layout="centered",
)

# Optional: warn if no API key (Cloud)
if not os.environ.get("OPENROUTER_API_KEY"):
    st.sidebar.warning(
        "OPENROUTER_API_KEY is not set on this deployment. "
        "The bot may rely more on simple KB answers."
    )

# Background GIF
gif_path = "pickleball.gif"
if os.path.exists(gif_path):
    with open(gif_path, "rb") as f:
        data = f.read()
        data_url = base64.b64encode(data).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/gif;base64,{data_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        h1, h2, h3 {{
            color: #000000;
            font-weight: 800;
        }}

        h3#ask-your-question {{
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 1.7rem !important;
        }}

        .stApp, .stMarkdown, label, p {{
            color: #111111 !important;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("Hello Pickleball")
st.caption("Beginner‑friendly answers to your pickleball questions.")

st.sidebar.title("How to use")
st.sidebar.write(
    "- Ask about **rules**: kitchen, scoring, serving.\n"
    "- Ask for **tips**: 'Give me 3 beginner tips'.\n"
    "- Ask about **equipment** or **famous players**.\n"
    "- Try casual things like 'hi' or 'explain pickleball game'."
)

st.subheader("Ask your question", anchor="ask-your-question")

with st.form("ask_form", enter_to_submit=True):
    question = st.text_input(
        "Type a pickleball question:",
        placeholder="Example: What is the kitchen rule?",
    )
    ask_clicked = st.form_submit_button("Ask")

if ask_clicked and question.strip():
    with st.spinner("Thinking..."):
        answer = pickleball_agent(question)

    st.markdown("### Answer")
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.92);
            padding: 1.25rem 1.5rem;
            border-radius: 0.8rem;
            max-width: 900px;
            margin: 0.5rem auto 1.5rem auto;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
            color: #111111;
            font-weight: 600;
            line-height: 1.4;
        ">
        {answer}
        </div>
        """,
        unsafe_allow_html=True,
    )
elif ask_clicked:
    st.warning("Please type a question before pressing Ask.")
