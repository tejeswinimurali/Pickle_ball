import os
import urllib3
from typing import Dict

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- Config ----------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openrouter/auto:online"  # router model

# ---------- Knowledge base ----------

PICKLEBALL_KB: Dict[str, Dict[str, str]] = {
    "rules": {
        "scoring": (
            "Standard games go to 11 points, win by 2. "
            "Only the serving team can score, and you call score as "
            "server score, receiver score, server number."
        ),
        "serving": (
            "Serve underhand from behind the baseline, diagonally cross-court, "
            "and the ball must clear the non-volley zone (kitchen) including the line."
        ),
        "two_bounce": (
            "After the serve, the ball must bounce once on the return and once on the next shot "
            "before anyone can volley. This is the two-bounce rule."
        ),
        "kitchen": (
            "The kitchen (non-volley zone) is a 7-foot area by the net. "
            "You may step in to hit a ball that has bounced, but you cannot volley "
            "while touching it or its line."
        ),
        "faults": (
            "Common faults: serve lands in the kitchen, ball out of bounds, ball into the net, "
            "ball bounces twice, or volleying from the kitchen."
        ),
        "singles_doubles": (
            "Singles is 1 vs 1, doubles is 2 vs 2. "
            "Serving order and court positioning change slightly, "
            "but the main rules are the same."
        ),
        "let_serve": (
            "Most modern play does not use lets on serves. If the serve clips the net "
            "but lands correctly, the ball is still in play."
        ),
    },
    "equipment": {
        "ball": (
            "A pickleball is a light plastic ball with holes. "
            "Outdoor balls are a bit harder with smaller holes; "
            "indoor balls are softer with larger holes."
        ),
        "paddle": (
            "Paddles are solid, usually composite or graphite, "
            "bigger than a ping-pong paddle and smaller than a tennis racket."
        ),
        "court": (
            "The court is 20 by 44 feet with a 7-foot non-volley zone on each side of the net. "
            "The same court size is used for singles and doubles."
        ),
        "shoes": (
            "Court shoes with good lateral support are best. "
            "Running shoes are not ideal because they are built for straight-line motion."
        ),
    },
    "tips": {
        "consistency": (
            "Play high-percentage shots: clear the net with a safe margin and keep the ball in. "
            "Winning at beginner level is mostly about fewer unforced errors."
        ),
        "dink": (
            "Practice soft dinks into the kitchen to slow the game down and force your opponents "
            "to hit up. Think smooth, relaxed swings rather than big power."
        ),
        "third_shot": (
            "On your team’s third shot, aim for a soft drop into the kitchen instead of blasting it. "
            "That gives you time to move to the net."
        ),
        "positioning": (
            "Try to get both partners up to the non-volley line together. "
            "Playing from the baseline all the time puts you at a big disadvantage."
        ),
        "communication": (
            "In doubles, call balls that are yours, shout 'mine' or 'yours', and decide in advance "
            "who takes middle balls and lobs."
        ),
        "footwork": (
            "Stay light on your feet, take small adjustment steps, "
            "and avoid crossing your feet when moving sideways."
        ),
    },
    "players": {
        "ben_johns": (
            "Ben Johns is one of the most successful pro pickleball players, "
            "known for his balanced offense and defense and multiple titles "
            "in singles and doubles."
        ),
        "anna_leigh_waters": (
            "Anna Leigh Waters is a top women's pro, famous for her aggressive style "
            "and dominance in singles, doubles, and mixed doubles."
        ),
        "other_notable": (
            "Other notable pros include Tyson McGuffin, JW Johnson, "
            "Riley Newman, and Catherine Parenteau."
        ),
    },
    "general": {
        "what_is": (
            "Pickleball is a paddle sport that mixes elements of tennis, badminton, "
            "and table tennis, played on a small court with a perforated plastic ball."
        ),
        "history": (
            "Pickleball began in 1965 on Bainbridge Island, Washington, "
            "as a backyard family game and has grown into a global sport with pro tours."
        ),
        "popularity": (
            "Pickleball is one of the fastest-growing sports, with millions of players "
            "and new courts popping up in parks, gyms, and clubs."
        ),
        "players_needed": (
            "You usually play pickleball with 2 players for singles (1 on each side) "
            "or 4 players for doubles (2 on each side)."
        ),
    },
}


def search_kb(question: str) -> str:
    """KB search logic."""
    q = question.lower()
    q = q.replace("pickle ball", "pickleball")

    if (
        "explain pickleball" in q
        or "pickleball game" in q
        or ("what is" in q and "pickleball" in q)
        or (q.strip() == "pickleball")
    ):
        return " ".join(
            [
                PICKLEBALL_KB["general"]["what_is"],
                PICKLEBALL_KB["rules"]["scoring"],
                PICKLEBALL_KB["rules"]["serving"],
            ]
        )

    if "how many players" in q or ("players" in q and "needed" in q):
        return PICKLEBALL_KB["general"]["players_needed"]

    if "beginner" in q or "first time" in q or "new to pickleball" in q:
        return " ".join(
            [
                PICKLEBALL_KB["general"]["what_is"],
                PICKLEBALL_KB["rules"]["scoring"],
                PICKLEBALL_KB["tips"]["consistency"],
            ]
        )

    if "famous" in q or "best" in q or "pro" in q or "professional" in q:
        return " ".join(PICKLEBALL_KB["players"].values())

    if "tip" in q or "improve" in q or "strategy" in q or "drill" in q:
        return " ".join(PICKLEBALL_KB["tips"].values())

    if "what is pickleball" in q or ("what" in q and "pickleball" in q):
        return PICKLEBALL_KB["general"]["what_is"]
    if "history" in q:
        return PICKLEBALL_KB["general"]["history"]
    if "popular" in q or "popularity" in q or "growing" in q:
        return PICKLEBALL_KB["general"]["popularity"]

    if "two bounce" in q or "double bounce" in q:
        return PICKLEBALL_KB["rules"]["two_bounce"]
    if "kitchen" in q or "non-volley" in q or "nvz" in q:
        return PICKLEBALL_KB["rules"]["kitchen"]
    if "score" in q or "scoring" in q or "points" in q:
        return PICKLEBALL_KB["rules"]["scoring"]
    if "serve" in q or "serving" in q or "server" in q:
        return PICKLEBALL_KB["rules"]["serving"]
    if "fault" in q or "error" in q or "violation" in q:
        return PICKLEBALL_KB["rules"]["faults"]
    if "let" in q and "serve" in q:
        return PICKLEBALL_KB["rules"]["let_serve"]
    if "single" in q or "doubles" in q:
        return PICKLEBALL_KB["rules"]["singles_doubles"]

    if "paddle" in q:
        return PICKLEBALL_KB["equipment"]["paddle"]
    if "ball" in q:
        return PICKLEBALL_KB["equipment"]["ball"]
    if "court" in q or "dimension" in q or "size" in q:
        return PICKLEBALL_KB["equipment"]["court"]
    if "shoe" in q or "shoes" in q:
        return PICKLEBALL_KB["equipment"]["shoes"]

    return "General pickleball info: " + " ".join(
        [
            PICKLEBALL_KB["general"]["what_is"],
            PICKLEBALL_KB["general"]["popularity"],
        ]
    )


# ---------- LangChain tool + agent ----------

@tool
def pickleball_kb_tool(question: str) -> str:
    """Answer pickleball questions from a curated knowledge base of rules, tips, equipment, and players."""
    return search_kb(question)


def build_llm() -> ChatOpenAI:
    """Create a LangChain ChatOpenAI client that talks to OpenRouter."""
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.7,
        max_tokens=220,
    )


def build_agent() -> AgentExecutor:
    """Initialize a LangChain agent that can call the KB tool."""
    llm = build_llm()
    tools = [pickleball_kb_tool]

    system_prompt = (
        "You are a super friendly, energetic pickleball coach who LOVES answering beginner questions.\n"
        "Only talk about pickleball. If the user asks about anything else, say you are a pickleball-only bot.\n"
        "First line: short, direct answer in a friendly tone. Then 3–6 short sentences with 1–2 practical tips."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    lc_agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=lc_agent, tools=tools, verbose=False)
    return executor


_AGENT = None  # cached agent


def get_agent() -> AgentExecutor:
    global _AGENT
    if _AGENT is None:
        _AGENT = build_agent()
    return _AGENT


def run_agent(question: str) -> str:
    """Entry point used by Streamlit: run the LangChain agent on a question."""
    agent = get_agent()
    result = agent.invoke({"input": question})
    # AgentExecutor returns a dict; final answer is usually under "output"
    return result.get("output", str(result))
