import base64
import streamlit as st
from pickleball_agent import pickleball_agent

# ---- Page config ----
st.set_page_config(
    page_title="Pickleball FAQ Bot",
    page_icon="🏓",
    layout="centered",
)

# ---- Full-page GIF background ----
with open("pickleball.gif", "rb") as f:  # file must be in the same folder as app.py
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

    /* Darker, thicker headings */
    h1, h2, h3 {{
        color: #000000;
        font-weight: 800;
    }}

    /* Make ONLY "Ask your question" darker & larger */
    h3#ask-your-question {{
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 1.7rem !important;  /* adjust as you like */
    }}

    /* Darker normal text and labels */
    .stApp, .stMarkdown, label, p {{
        color: #111111 !important;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- Main content ----
st.title("Hello Pickleball")
st.caption("Beginner-friendly answers to your pickleball questions.")

st.write("")

st.sidebar.title("How to use")
st.sidebar.write(
    "- Ask about rules: kitchen, scoring, serving.\n"
    "- Ask for tips: *Give me 3 beginner tips*.\n"
    "- Ask about equipment or players."
)

# ---- Ask your question ----
st.subheader("Ask your question")

# Put input + button inside a form
with st.form("ask_form", enter_to_submit=True):
    question = st.text_input(
        "Type a pickleball question:",
        placeholder="Example: What is the kitchen rule?",
    )

    ask_clicked = st.form_submit_button("Ask")  # this is now the Ask button

# ---- Show answer with automatic white faded background ----
if ask_clicked and question.strip():
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
        ">
        {answer}
        </div>
        """,
        unsafe_allow_html=True,
    )

elif ask_clicked:
    st.warning("Please type a question before pressing Ask.")
