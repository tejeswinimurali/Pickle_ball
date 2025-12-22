import os
import urllib3
from typing import Dict

from langchain.tools import tool
from langchain_openai import ChatOpenAI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct:free"  # free model on OpenRouter [web:1074]

# ---------- Knowledge base (fallback only) ----------

SPORTS_KB: Dict[str, Dict[str, str]] = {
    "general": {
        "what_is_sport": (
            "Sport is any kind of physical activity or game that usually involves "
            "individuals or teams competing against each other for fun, exercise, "
            "or organized competition."
        ),
        "benefits": (
            "Playing sports improves fitness, coordination, and mental health. "
            "It helps with discipline, teamwork, managing stress, and building confidence."
        ),
        "types": (
            "There are many types of sports: team sports like football and basketball, "
            "racket sports like tennis and badminton, bat-and-ball sports like cricket and baseball, "
            "and individual sports like athletics and swimming."
        ),
    },
    "football": {
        "basic_rules": (
            "Football (soccer) is played by two teams of 11 players. "
            "You score by getting the ball into the opponent's goal using any body part "
            "except hands and arms, unless you are the goalkeeper."
        ),  # [web:1025]
        "equipment": (
            "Basic football equipment: a football, jerseys, shorts, socks, shin guards, and boots "
            "with studs or cleats for grip on the pitch."
        ),  # [web:1034]
        "famous_players": (
            "Some famous footballers include Lionel Messi, Cristiano Ronaldo, "
            "Neymar Jr, Kylian Mbappé, and Sunil Chhetri."
        ),
    },
    "basketball": {
        "basic_rules": (
            "Basketball is played by two teams of five players on the court. "
            "You score by throwing the ball through the opponent's hoop. "
            "You must dribble while moving; carrying or double-dribbling is not allowed."
        ),
        "equipment": (
            "You need a basketball, an indoor or outdoor court with hoops, "
            "and supportive court shoes for quick changes of direction."
        ),
        "famous_players": (
            "Famous basketball players include Michael Jordan, LeBron James, "
            "Kobe Bryant, Stephen Curry, and Giannis Antetokounmpo."
        ),
    },
    "tennis": {
        "basic_rules": (
            "Tennis can be played singles (1 vs 1) or doubles (2 vs 2). "
            "Players hit a ball over a net into the opponent's court. "
            "Points follow the sequence 15, 30, 40, and game."
        ),
        "equipment": (
            "You need a tennis racket, tennis balls, and a court with a net. "
            "Tennis shoes with good lateral support are recommended."
        ),  # [web:1037]
        "famous_players": (
            "Famous tennis players include Roger Federer, Rafael Nadal, "
            "Novak Djokovic, Serena Williams, and Iga Świątek."
        ),
    },
    "cricket": {
        "basic_rules": (
            "Cricket is played between two teams of eleven players. "
            "One team bats to score runs, while the other bowls and fields to restrict runs "
            "and dismiss batters."
        ),
        "equipment": (
            "Key cricket equipment: bat, hard leather ball, stumps and bails, "
            "protective pads, gloves, helmet, and appropriate footwear."
        ),  # [web:1040]
        "famous_players": (
            "Well-known cricketers include Sachin Tendulkar, Virat Kohli, "
            "MS Dhoni, Ben Stokes, and Ellyse Perry."
        ),
    },
    "training_tips": {
        "beginners": (
            "If you are new to sports, start with simple drills, warm up properly, "
            "and focus on technique before intensity. Aim for consistent practice "
            "2–3 times per week."
        ),
        "fitness": (
            "Combine cardio, strength work, and mobility exercises to support performance "
            "and reduce injury risk."
        ),
        "mindset": (
            "Set small, realistic goals, track progress, and remember improvement takes time. "
            "Focus on learning and enjoyment, not just winning."
        ),
    },
    "injury_prevention": {
        "warmup": (
            "Always warm up 5–10 minutes with light movement and dynamic stretches "
            "before playing to prepare your muscles and joints."
        ),
        "cooldown": (
            "Cool down after playing with easy walking and stretching to help recovery "
            "and reduce stiffness."
        ),
        "safety": (
            "Use appropriate protective gear, stay hydrated, and stop if you feel sharp pain. "
            "Rest and proper technique are key to avoiding overuse injuries."
        ),
    },
}


def search_kb(question: str) -> str:
    """Very simple rules to build a fallback answer when online fails."""
    q = question.lower()

    if "what is sport" in q or ("what is" in q and "sport" in q):
        return " ".join(
            [
                SPORTS_KB["general"]["what_is_sport"],
                SPORTS_KB["general"]["types"],
                SPORTS_KB["general"]["benefits"],
            ]
        )

    if "benefit" in q or "good for health" in q or "why play sports" in q:
        return " ".join(
            [
                SPORTS_KB["general"]["benefits"],
                SPORTS_KB["training_tips"]["beginners"],
            ]
        )

    if "football" in q or "soccer" in q:
        return " ".join(
            [
                SPORTS_KB["football"]["basic_rules"],
                SPORTS_KB["football"]["equipment"],
                SPORTS_KB["football"]["famous_players"],
            ]
        )

    if "basketball" in q:
        return " ".join(
            [
                SPORTS_KB["basketball"]["basic_rules"],
                SPORTS_KB["basketball"]["equipment"],
                SPORTS_KB["basketball"]["famous_players"],
            ]
        )

    if "tennis" in q:
        return " ".join(
            [
                SPORTS_KB["tennis"]["basic_rules"],
                SPORTS_KB["tennis"]["equipment"],
                SPORTS_KB["tennis"]["famous_players"],
            ]
        )

    if "cricket" in q:
        return " ".join(
            [
                SPORTS_KB["cricket"]["basic_rules"],
                SPORTS_KB["cricket"]["equipment"],
                SPORTS_KB["cricket"]["famous_players"],
            ]
        )

    if "tip" in q or "improve" in q or "practice" in q or "training" in q:
        return " ".join(SPORTS_KB["training_tips"].values())

    if "injury" in q or "hurt" in q or "pain" in q or "safe" in q:
        return " ".join(SPORTS_KB["injury_prevention"].values())

    if "famous" in q or "best player" in q or "legend" in q:
        return " ".join(
            [
                SPORTS_KB["football"]["famous_players"],
                SPORTS_KB["basketball"]["famous_players"],
                SPORTS_KB["tennis"]["famous_players"],
                SPORTS_KB["cricket"]["famous_players"],
            ]
        )

    return "General sports info: " + " ".join(
        [
            SPORTS_KB["general"]["what_is_sport"],
            SPORTS_KB["general"]["types"],
            SPORTS_KB["general"]["benefits"],
        ]
    )


@tool
def sports_kb_tool(question: str) -> str:
    """Fallback sports answer from a small offline knowledge base."""
    return search_kb(question)


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.7,
        max_tokens=220,
    )  # [web:1031]


def run_agent(question: str) -> str:
    """
    Online-first strategy:
    - Try OpenRouter model (which can use its own training + web tools).
    - If the call fails (no key, 402, timeout, etc.), fall back to KB.
    """
    fallback_answer = sports_kb_tool.run(question)

    # If no key at all → immediate KB
    if not OPENROUTER_API_KEY:
        return fallback_answer

    llm = build_llm()

    # System + user messages so model is friendly and conversational
    messages = [
        (
            "system",
            "You are a super friendly, energetic multi-sport coach with internet access. "
            "Answer using up-to-date sports knowledge from your training and any tools you have. "
            "If the user just greets you (hi, hello, thanks, etc.), greet them back warmly "
            "before giving any extra information.",
        ),
        ("user", question),
    ]

    # Convert to LangChain format
    from langchain_core.messages import SystemMessage, HumanMessage  # type: ignore

    lc_messages = [
        SystemMessage(content=messages[0][1]),
        HumanMessage(content=messages[1][1]),
    ]

    try:
        resp = llm.invoke(lc_messages)
        return resp.content
    except Exception:
        # Any error → safe KB answer instead of crashing
        return fallback_answer
