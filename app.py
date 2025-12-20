# app.py
import os
import streamlit as st

from agent import run_agent, OPENROUTER_API_KEY

st.set_page_config(page_title="Pickleball FAQ Coach", page_icon="🏓")

st.title("Pickleball FAQ Coach 🏓")
st.write(
    "Ask anything about pickleball rules, equipment, tips, or famous players. "
    "This bot uses a pickleball knowledge base plus an OpenRouter-powered LLM."
)

# Environment warning
if not OPENROUTER_API_KEY:
    st.warning(
        "OPENROUTER_API_KEY is not set on this deployment. "
        "The bot may rely more on simple KB-style answers."
    )

# Simple chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_input = st.chat_input("Ask a pickleball question...")
if user_input:
    # Show user message
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Coach is thinking..."):
            try:
                answer = run_agent(user_input)
            except Exception as e:
                answer = (
                    "Oops, something went wrong with the online model. "
                    "Here is a basic KB answer instead.\n\n"
                )
                # Optional: you could call search_kb here directly if you import it.

            st.markdown(answer)
            st.session_state.messages.append(("assistant", answer))

st.sidebar.header("How to use")
st.sidebar.markdown(
    """
- Ask about **rules**: kitchen, scoring, serving, faults.
- Ask for **tips**: dinks, third shot, positioning, drills.
- Ask about **equipment**: paddles, balls, shoes, court size.
- Ask about **players**: Ben Johns, Anna Leigh Waters, etc.
"""
)
