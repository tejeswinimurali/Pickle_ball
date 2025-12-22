import os
import requests
import streamlit as st

from agent import run_agent  # make sure this import path is correct

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Sports FAQ Bot",
    page_icon="🏅",
    layout="centered",
)  # [web:995]

# Optional: light styling for a white card in the center
st.markdown(
    """
    <style>
    .main-card {
        background-color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .main-title {
        text-align: center;
    }
    .subtext {
        text-align: center;
        color: #555555;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)  # [web:961]

# Wrap whole UI in a "card"
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # -----------------------------
    # Header
    # -----------------------------
    st.markdown('<h1 class="main-title">🏅 Sports FAQ Bot</h1>', unsafe_allow_html=True)

    st.markdown(
        '<p class="subtext">'
        'Ask anything about sports rules, equipment, training tips, or famous players across different sports. '
        'This bot uses a sports knowledge base plus an OpenRouter-powered LLM.'
        '</p>',
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Small GIF under intro (online, no local file needed)
    # -----------------------------
    st.image(
        "https://media.giphy.com/media/l0HlRnAWXxn0MhKLK/giphy.gif",
        caption="Let’s talk sports!",
        width=220,
    )  # [web:1051]

    st.markdown("---")

    # -----------------------------
    # Sidebar settings
    # -----------------------------
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox(
            "Model (display only, main logic uses free Llama 3.1 8B)",
            [
                "meta-llama/llama-3.1-8b-instruct:free",
            ],
            index=0,
        )
        temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.7, 0.1)

    # -----------------------------
    # Chat history
    # -----------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -----------------------------
    # User input
    # -----------------------------
    user_input = st.chat_input("Ask your sports question...")
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # -----------------------------
        # Call agent (handles KB + OpenRouter)
        # -----------------------------
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Thinking..._")

            try:
                reply = run_agent(user_input)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"

            placeholder.markdown(reply)

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": reply})

    st.markdown("</div>", unsafe_allow_html=True)
