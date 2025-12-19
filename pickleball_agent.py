import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    "api_key": os.environ.get(
        "OPENROUTER_API_KEY",
        "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",
    ),
    "api_base": "https://openrouter.ai/api/v1",
    "model": "openrouter/auto:online",  # web-enabled router model
    "max_tokens": 220,
}


def call_openrouter_api(messages, temperature=0.7):
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
        "plugins": [
            {
                "id": "web",
                "max_results": 3,
            }
        ],
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
            "Standard games go to 11 points, win by 2. "
            "Only the serving team can score, and you call score as server score, receiver score, server number."
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
            "You may step in to hit a ball that has bounced, but you cannot volley while touching it or its line."
        ),
        "faults": (
            "Common faults: serve lands in the kitchen, ball out of bounds, ball into the net, "
            "ball bounces twice, or volleying from the kitchen."
        ),
        "singles_doubles": (
            "Singles is 1 vs 1, doubles is 2 vs 2. "
            "Serving order and court positioning change slightly, but the main rules are the same."
        ),
        "let_serve": (
            "Most modern play does not use lets on serves. If the serve clips the net but lands correctly, "
            "the ball is still in play."
        ),
    },
    "equipment": {
        "ball": (
            "A pickleball is a light plastic ball with holes. "
            "Outdoor balls are a bit harder with smaller holes; indoor balls are softer with larger holes."
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
            "Practice soft dinks into the kitchen to slow the game down and force your opponents to hit up. "
            "Think smooth, relaxed swings rather than big power."
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
            "In doubles, call balls that are yours, shout 'mine' or 'yours', and decide in advance who takes "
            "middle balls and lobs."
        ),
        "footwork": (
            "Stay light on your feet, take small adjustment steps, and avoid crossing your feet when moving sideways."
        ),
    },
    "players": {
        "ben_johns": (
            "Ben Johns is one of the most successful pro pickleball players, "
            "known for his balanced offense and defense and multiple titles in singles and doubles."
        ),
        "anna_leigh_waters": (
            "Anna Leigh Waters is a top women's pro, famous for her aggressive style "
            "and dominance in singles, doubles, and mixed doubles."
        ),
        "other_notable": (
            "Other notable pros include Tyson McGuffin, JW Johnson, Riley Newman, and Catherine Parenteau."
        ),
    },
    "general": {
        "what_is": (
            "Pickleball is a paddle sport that mixes elements of tennis, badminton, and table tennis, "
            "played on a small court with a perforated plastic ball."
        ),
        "history": (
            "Pickleball began in 1965 on Bainbridge Island, Washington, as a backyard family game and "
            "has grown into a global sport with pro tours."
        ),
        "popularity": (
            "Pickleball is one of the fastest-growing sports, with millions of players and new courts "
            "popping up in parks, gyms, and clubs."
        ),
        "players_needed": (
            "You usually play pickleball with 2 players for singles (1 on each side) "
            "or 4 players for doubles (2 on each side)."
        ),
    },
}


def search_kb(question: str) -> str:
    q = question.lower()
    q = q.replace("pickle ball", "pickleball")

    # General "explain pickleball" intent FIRST (so it doesn't fall into 'ball')
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

    # Number of players
    if "how many players" in q or ("players" in q and "needed" in q):
        return PICKLEBALL_KB["general"]["players_needed"]

    # Explicit beginner intent
    if "beginner" in q or "first time" in q or "new to pickleball" in q:
        return " ".join(
            [
                PICKLEBALL_KB["general"]["what_is"],
                PICKLEBALL_KB["rules"]["scoring"],
                PICKLEBALL_KB["tips"]["consistency"],
            ]
        )

    # Famous players
    if "famous" in q or "best" in q or "pro" in q or "professional" in q:
        return " ".join(PICKLEBALL_KB["players"].values())

    # Tips / coaching
    if "tip" in q or "improve" in q or "strategy" in q or "drill" in q:
        return " ".join(PICKLEBALL_KB["tips"].values())

    # General info
    if "what is pickleball" in q or ("what" in q and "pickleball" in q):
        return PICKLEBALL_KB["general"]["what_is"]
    if "history" in q:
        return PICKLEBALL_KB["general"]["history"]
    if "popular" in q or "popularity" in q or "growing" in q:
        return PICKLEBALL_KB["general"]["popularity"]

    # Rules
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

    # Equipment
    if "paddle" in q:
        return PICKLEBALL_KB["equipment"]["paddle"]
    if "ball" in q:
        return PICKLEBALL_KB["equipment"]["ball"]
    if "court" in q or "dimension" in q or "size" in q:
        return PICKLEBALL_KB["equipment"]["court"]
    if "shoe" in q or "shoes" in q:
        return PICKLEBALL_KB["equipment"]["shoes"]

    # Fallback: generic info, so online model still has context
    return "General pickleball info: " + " ".join(
        [
            PICKLEBALL_KB["general"]["what_is"],
            PICKLEBALL_KB["general"]["popularity"],
        ]
    )


def pickleball_agent(question: str) -> str:
    # If the question is clearly NOT about pickleball, let the model say that
    lower_q = question.lower()
    if "pickle" not in lower_q and "paddle" not in lower_q and "court" not in lower_q:
        system_prompt = """
You are a friendly pickleball coach. 
If the user asks about something that is NOT related to pickleball, politely say:
"I'm your pickleball buddy, so I can only help with pickleball stuff."
Do not answer non-pickleball questions.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        answer = call_openrouter_api(messages, temperature=0.7)
        return answer

    kb_info = search_kb(question)

    SYSTEM_PROMPT = """
You are a super friendly, energetic pickleball coach who LOVES answering beginner questions.

Tone:
- Start warmly when it fits: "Love this question!", "Happy to help!", etc.
- Sound encouraging and positive.
- Keep language casual and simple.

Answer style:
- First line: short, direct answer in a friendly tone.
- Then 3–6 short sentences or a few bullets explaining the why/how with 1–2 practical tips.

Knowledge:
- Use the KB info given plus any web results.
- Stick strictly to pickleball topics.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"User question: {question}\n\nKB info: {kb_info}",
        },
    ]

    answer = call_openrouter_api(messages, temperature=0.7)

    # If online model fails, fall back to KB info
    if isinstance(answer, str) and "online model failed" in answer:
        return kb_info

    return answer
