import os
import requests
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Pickleball Pro Bot",
    page_icon="🏓",
    layout="centered",
)

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
    st.markdown('<h1 class="main-title">🏓 Pickleball Pro Bot</h1>', unsafe_allow_html=True)

    st.markdown(
        '<p class="subtext">'
        'Ask anything about pickleball rules, equipment, tips, or famous players. '
        'This bot uses a pickleball knowledge base plus an OpenRouter-powered LLM.'
        '</p>',
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Small GIF under intro
    # -----------------------------
    # Option A: local GIF (put pickleball.gif in same folder as app.py)
    st.image(
        "pickleball.gif",
        caption="Let’s play pickleball!",
        width=200,
    )  # [web:945]

    st.markdown("---")

    # -----------------------------
    # Your existing app content
    # -----------------------------

    # Example: sidebar model + temperature controls
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox(
            "Model",
            ["meta-llama/llama-3.1-70b-instruct", "gpt-4.1-mini"],
            index=0,
        )
        temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.7, 0.1)

    # Chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_input = st.chat_input("Ask your pickleball question...")
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # Call your OpenRouter + knowledge base backend
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Thinking..._")

            try:
                # -----------------------------
                # Replace this with your current OpenRouter call
                # -----------------------------
                OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                }

                # Example payload; plug in your existing retrieval / system prompt
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful pickleball expert assistant.",
                        },
                        *st.session_state.messages,
                    ],
                    "temperature": temperature,
                }

                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"

            placeholder.markdown(reply)

            # Save assistant reply to history
            st.session_state.messages.append({"role": "assistant", "content": reply})

    st.markdown("</div>", unsafe_allow_html=True)
