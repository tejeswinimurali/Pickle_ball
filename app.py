import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="Sports FAQ Bot",
    page_icon="🏅",
    layout="centered",
)

st.markdown(
    """
    <style>
    /* Kill ALL default header/toolbar/decoration, including background strip */
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Remove extra margin that was under the header */
    section[data-testid="stMain"] {
        padding-top: 0 !important;
    }

    section[data-testid="stMain"] > div.block-container {
        padding-top: 0.1rem;
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
)  # [web:1179][web:1100]

st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🏅 Sports FAQ Bot</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtext">'
    'Chat about sports rules, equipment, training tips, or famous players across different sports. '
    'This bot uses an online OpenRouter model, with a small sports knowledge base as backup.'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# chat history + input exactly as you already have below...
