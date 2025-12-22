import os
import urllib3
from typing import Dict

from langchain.tools import tool
from langchain_openai import ChatOpenAI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Use a free / unpaid model
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct:free"  # [web:1063][web:1074]

# ---------- Knowledge base ----------

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
        "duration": (
            "A standard match is 90 minutes, split into two 45-minute halves, "
            "plus stoppage time added by the referee."
        ),
        "fouls": (
            "Fouls are given for actions like tripping, pushing, or handball. "
            "Serious fouls can result in yellow or red cards."
        ),
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
        "duration": (
            "Games are usually played in four quarters, each commonly 10 or 12 minutes long "
            "depending on the league."
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
            "Combine cardio (jogging, cycling), strength work (bodyweight or light weights), "
            "and mobility exercises to support performance and reduce injury risk."
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
    q = question.lower()

    # General sports questions
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

    # Football
    if "football" in q or "soccer" in q:
        pieces = [SPORTS_KB["football"]["basic_rules"]]
        if "equipment" in q or "need" in q:
            pieces.append(SPORTS_KB["football"]["equipment"])
        if "time" in q or "how long" in q or "duration" in q:
            pieces.append(SPORTS_KB["football"]["duration"])
        if "foul" in q or "card" in q:
            pieces.append(SPORTS_KB["football"]["fouls"])
        if "famous" in q or "best" in q or "player" in q:
            pieces.append(SPORTS_KB["football"]["famous_players"])
        return " ".join(pieces)

    # Basketball
    if "basketball" in q:
        pieces = [SPORTS_KB["basketball"]["basic_rules"]]
        if "equipment" in q or "need" in q:
            pieces.append(SPORTS_KB["basketball"]["equipment"])
        if "time" in q or "how long" in q or "duration" in q:
            pieces.append(SPORTS_KB["basketball"]["duration"])
        if "famous" in q or "best" in q or "player" in q:
            pieces.append(SPORTS_KB["basketball"]["famous_players"])
        return " ".join(pieces)

    # Tennis
    if "tennis" in q:
        pieces = [SPORTS_KB["tennis"]["basic_rules"]]
        if "equipment" in q or "need" in q:
            pieces.append(SPORTS_KB["tennis"]["equipment"])
        if "famous" in q or "best" in q or "player" in q:
            pieces.append(SPORTS_KB["tennis"]["famous_players"])
        return " ".join(pieces)

    # Cricket
    if "cricket" in q:
        pieces = [SPORTS_KB["cricket"]["basic_rules"]]
        if "equipment" in q or "need" in q:
            pieces.append(SPORTS_KB["cricket"]["equipment"])
        if "famous" in q or "best" in q or "player" in q:
            pieces.append(SPORTS_KB["cricket"]["famous_players"])
        return " ".join(pieces)

    # Training / fitness / generic tips
    if "tip" in q or "improve" in q or "practice" in q or "training" in q:
        return " ".join(SPORTS_KB["training_tips"].values())

    if "injury" in q or "hurt" in q or "pain" in q or "safe" in q:
        return " ".join(SPORTS_KB["injury_prevention"].values())

    # Famous players – generic
    if "famous" in q or "best player" in q or "legend" in q:
        return " ".join(
            [
                SPORTS_KB["football"]["famous_players"],
                SPORTS_KB["basketball"]["famous_players"],
                SPORTS_KB["tennis"]["famous_players"],
                SPORTS_KB["cricket"]["famous_players"],
            ]
        )

    # Fallback: general sports info
    return "General sports info: " + " ".join(
        [
            SPORTS_KB["general"]["what_is_sport"],
            SPORTS_KB["general"]["types"],
            SPORTS_KB["general"]["benefits"],
        ]
    )


@tool
def sports_kb_tool(question: str) -> str:
    """Answer sports questions from a curated knowledge base of rules, tips, equipment, and famous players across multiple sports."""
    return search_kb(question)


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.7,
        max_tokens=220,
    )  # [web:1090]


def run_agent(question: str) -> str:
    """
    Simple 'agentic' behavior:
    - Always fetch KB info with the tool.
    - Let the LLM turn it into a friendly answer when online.
    - If online fails, fall back cleanly to the KB answer.
    """
    kb_answer = sports_kb_tool.run(question)

    # Pure KB mode if key is missing
    if not OPENROUTER_API_KEY:
        return kb_answer

    llm = build_llm()
    prompt = (
        "You are a super friendly, energetic multi-sport coach for beginners.\n"
        "Use the sports knowledge base info below plus the user's question to answer.\n\n"
        f"User question: {question}\n"
        f"Sports KB info: {kb_answer}\n\n"
        "First line: short, direct answer in a friendly tone.\n"
        "Then 3–6 short sentences with 1–2 practical tips or clarifications.\n"
        "If something is outside this KB, still give a simple, best-effort explanation "
        "based on general sports knowledge.\n"
    )

    try:
        resp = llm.invoke(prompt)
        return resp.content
    except Exception:
        # If online model fails (including 402 Payment Required), fall back to KB
        return kb_answer
