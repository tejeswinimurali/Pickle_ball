import streamlit as st
from agent import run_agent

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Sports FAQ Bot",
    page_icon="🏅",
    layout="centered",
)

# -----------------------------
# Global CSS: tighten layout
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
        max-width: 820px;
    }
    .main-card {
        background-color: white;
        padding: 1.0rem 1.8rem 1.4rem 1.8rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .main-title {
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtext {
        text-align: center;
        color: #555555;
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
    }
    hr {
        margin: 0.4rem 0 0.6rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)  # [web:1100][web:1104]

# -----------------------------
# Card container
# -----------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🏅 Sports FAQ Bot</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtext">'
    'Ask anything about sports rules, equipment, training tips, or famous players across different sports. '
    'This bot uses a sports knowledge base plus an OpenRouter-powered LLM.'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# -----------------------------
# Chat history (scrolls above)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Input – last element on page
# -----------------------------
user_input = st.chat_input("Ask your sports question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")

        try:
            reply = run_agent(user_input)
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"

        placeholder.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

st.markdown("</div>", unsafe_allow_html=True)
