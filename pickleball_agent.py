import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    # Prefer loading from environment; you can also hard-code while testing
    "api_key": os.environ.get(
        "OPENROUTER_API_KEY",
        "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",
    ),
    "api_base": "https://openrouter.ai/api/v1",
    "model": "openrouter/auto",
    "max_tokens": 200,
}


def call_openrouter_api(messages, temperature=0.5):
    headers = {
        "Authorization": f"Bearer {CONFIG['api_key']}",
        "HTTP-Referer": "https://pickleball-chatbot.local",
        "X-Title": "Pickleball FAQ Agent",
    }
    payload = {
        "model": CONFIG["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": CONFIG["max_tokens"],
    }
    resp = requests.post(
        f"{CONFIG['api_base']}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
        verify=False,
    )

    data = resp.json()

    if "choices" not in data:
        err = data.get("error", {})
        msg = err.get("message", "unknown error")
        code = err.get("code", "no code")
        return f"Sorry, the online model failed (code {code}: {msg}). Please try again."

    return data["choices"][0]["message"]["content"]


PICKLEBALL_KB = {
    "rules": {
        "scoring": (
            "Games are usually played to 11 points, win by 2. "
            "Only the serving team can score."
        ),
        "serving": (
            "Serve underhand from behind the baseline, diagonally cross-court, "
            "and clear the non-volley zone."
        ),
        "kitchen": (
            "The kitchen (non-volley zone) is a 7-foot area by the net. "
            "You cannot volley while touching it or its line."
        ),
        "double_bounce": (
            "After the serve, the ball must bounce once on each side "
            "before anyone can volley."
        ),
        "faults": (
            "Faults include: hitting out, into the net, volleying from the kitchen, "
            "or missing the serve."
        ),
        "singles_doubles": (
            "Singles is 1 vs 1. Doubles is 2 vs 2. "
            "Scoring and serving rotations change slightly between them."
        ),
    },
    "equipment": {
        "ball": (
            "A pickleball is a light plastic ball with holes, "
            "with different types for indoor and outdoor play."
        ),
        "paddle": (
            "Paddles are solid, usually composite or graphite, "
            "larger than a ping-pong paddle and smaller than a tennis racket."
        ),
        "court": (
            "The court is 20 by 44 feet with a 7-foot non-volley zone "
            "on each side of the net. Same size for singles and doubles."
        ),
    },
    "tips": {
        "consistency": (
            "Aim for safe, consistent shots instead of constant winners, "
            "especially as a beginner."
        ),
        "dink": (
            "Practice soft dinks into the kitchen to control pace "
            "and force opponents to hit up."
        ),
        "positioning": (
            "Move to the non-volley line as soon as it is safe "
            "and try to play most rallies from there."
        ),
        "strategy": (
            "Communicate with your partner, attack weaker sides, and keep the ball low."
        ),
        "footwork": (
            "Use small, balanced steps and stay on the balls of your feet "
            "to move quickly."
        ),
    },
    "players": {
        "ben_johns": (
            "Ben Johns is a leading professional pickleball player "
            "and multi-time champion."
        ),
        "anna_leigh_waters": (
            "Anna Leigh Waters is a top professional known for dominating "
            "women's singles and doubles."
        ),
    },
    "general": {
        "what_is": (
            "Pickleball is a paddle sport combining tennis, badminton, and table "
            "tennis, played on a small court with a perforated plastic ball."
        ),
        "history": (
            "Pickleball started in 1965 on Bainbridge Island, Washington, "
            "as a backyard game and grew into a worldwide sport."
        ),
        "popularity": (
            "Millions now play pickleball, with community courts, leagues, "
            "and professional tours."
        ),
        "players_needed": (
            "Pickleball is normally played with 2 players for singles "
            "(1 on each side) or 4 players for doubles (2 on each side)."
        ),
    },
}


def search_kb(question: str) -> str:
    q = question.lower()
    q = q.replace("pickle ball", "pickleball")

    # Exact "how many players" style
    if "how many players" in q or ("players" in q and "needed" in q):
        return PICKLEBALL_KB["general"]["players_needed"]

    # Players (pros)
    if "famous" in q or "best" in q or "pro" in q or "professional" in q:
        return " ".join(PICKLEBALL_KB["players"].values())

    # Tips / coaching
    if "tip" in q or "beginner" in q or "improve" in q or "strategy" in q:
        return " ".join(PICKLEBALL_KB["tips"].values())

    # General
    if "what is pickleball" in q or ("what" in q and "pickleball" in q):
        return PICKLEBALL_KB["general"]["what_is"]
    if "history" in q:
        return PICKLEBALL_KB["general"]["history"]
    if "popular" in q or "popularity" in q or "growing" in q:
        return PICKLEBALL_KB["general"]["popularity"]

    # Rules
    if "kitchen" in q or "non-volley" in q or "nvz" in q:
        return PICKLEBALL_KB["rules"]["kitchen"]
    if "score" in q or "scoring" in q or "points" in q:
        return PICKLEBALL_KB["rules"]["scoring"]
    if "serve" in q or "serving" in q or "server" in q:
        return PICKLEBALL_KB["rules"]["serving"]
    if "double bounce" in q or ("double" in q and "bounce" in q):
        return PICKLEBALL_KB["rules"]["double_bounce"]
    if "fault" in q or "error" in q or "violation" in q:
        return PICKLEBALL_KB["rules"]["faults"]
    if "single" in q or "doubles" in q:
        return PICKLEBALL_KB["rules"]["singles_doubles"]

    # Equipment
    if "paddle" in q:
        return PICKLEBALL_KB["equipment"]["paddle"]
    if "ball" in q:
        return PICKLEBALL_KB["equipment"]["ball"]
    if "court" in q or "dimension" in q or "size" in q:
        return PICKLEBALL_KB["equipment"]["court"]

    # Fallback
    return "No exact fact found in the knowledge base; answer from general pickleball understanding."


def pickleball_agent(question: str) -> str:
    kb_info = search_kb(question)

    SYSTEM_PROMPT = """
You are a friendly pickleball coach for beginners.

Your job:
- Answer ONLY questions about pickleball rules, how to play, equipment, courts, and players.
- Use the KB info as the main truth. You may add a few simple extra details as long as they do not conflict with the KB.
- Give clear, encouraging explanations in 2–6 short sentences.
- Start with a direct answer in the first sentence, then briefly explain why or how.
- If KB info says there is no exact fact, answer from general pickleball knowledge but keep it beginner friendly.
- If the question is not about pickleball, say: "I only answer pickleball questions. Please ask about pickleball."
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"User question: {question}\n\nKB info: {kb_info}",
        },
    ]

    answer = call_openrouter_api(messages, temperature=0.5)

    if isinstance(answer, str) and "online model failed" in answer:
        # fall back to plain KB text
        return kb_info

    return answer
