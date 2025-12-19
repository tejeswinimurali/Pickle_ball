import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    "api_key": "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",
    "api_base": "https://openrouter.ai/api/v1",
    "model": "openrouter/auto",
    "max_tokens": 128,
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
        # nice human-readable error
        err = data.get("error", {})
        msg = err.get("message", "unknown error")
        code = err.get("code", "no code")
        return f"Sorry, the online model failed (code {code}: {msg}). Please try again."

    return data["choices"][0]["message"]["content"]

PICKLEBALL_KB = {
    "rules": {
        "scoring": "Pickleball games are usually played to 11 points, win by 2. Only the serving team can score a point during their service turn.",
        "serving": "Serve underhand from behind the baseline, diagonally cross‑court, with at least one foot behind the line. The serve must clear the non‑volley zone (kitchen).",
        "kitchen": "The kitchen (non‑volley zone) is a 7‑foot area on both sides of the net. You cannot volley the ball while touching the kitchen or its line, but you may enter it to play a ball that has bounced.",
        "double_bounce": "After the serve, the ball must bounce once on each side before players are allowed to volley. This is called the double‑bounce rule.",
        "faults": "Common faults are: hitting the ball out of bounds, into the net, volleying from the kitchen, or missing the ball on a serve.",
        "singles_doubles": "Rules are almost the same for singles and doubles. The main difference is how you position and rotate servers in doubles.",
    },
    "equipment": {
        "ball": "A pickleball is a lightweight plastic ball with holes, different designs for indoor and outdoor play.",
        "paddle": "Paddles are solid (no strings), usually made from composite, graphite, or wood, and larger than a ping‑pong paddle but smaller than a tennis racket.",
        "court": "A pickleball court is 20 by 44 feet, with a non‑volley zone (kitchen) that is 7 feet from the net on each side. The same court size is used for singles and doubles.",
    },
    "tips": {
        "consistency": "Aim for safe, consistent shots instead of trying to hit winners on every ball, especially as a beginner.",
        "dink": "Practice soft dinks into the kitchen to control the pace and force your opponents to hit up on the ball.",
        "positioning": "Move up to the non‑volley line as soon as it is safe after the return, and try to play from there most of the rally.",
        "strategy": "Communicate with your partner, aim for your opponents’ weaker side, and keep balls low over the net.",
        "footwork": "Use small, balanced steps and stay on the balls of your feet so you can move quickly in any direction.",
    },
    "players": {
        "ben_johns": "Ben Johns is one of the most famous professional pickleball players and a multiple‑time champion in singles and doubles.",
        "anna_leigh_waters": "Anna Leigh Waters is a top professional pickleball player known for dominating women's singles and doubles events.",
    },
    "general": {
        "what_is": "Pickleball is a paddle sport that combines elements of tennis, badminton, and table tennis, played on a small court with a perforated plastic ball.",
        "history": "Pickleball was invented in 1965 on Bainbridge Island, Washington, as a backyard game and has since grown into a popular sport worldwide.",
        "popularity": "Pickleball has rapidly grown in popularity with millions of players, many community courts, and professional tours and tournaments.",
    },
}
def search_kb(question: str) -> str:
    q = question.lower()

    # Normalize some common phrases
    q = q.replace("pickle ball", "pickleball")

    # ---- High‑priority intent matches ----
    # Players
    if "player" in q or "pro" in q or "professional" in q or "famous" in q:
        return " ".join(PICKLEBALL_KB["players"].values())

    # Tips / coaching
    if "tip" in q or "beginner" in q or "improve" in q or "strategy" in q or "how do i get better" in q:
        return " ".join(PICKLEBALL_KB["tips"].values())

    # What is pickleball / general info
    if "what is pickleball" in q or ("what" in q and "pickleball" in q):
        return PICKLEBALL_KB["general"]["what_is"]
    if "history" in q:
        return PICKLEBALL_KB["general"]["history"]
    if "popular" in q or "popularity" in q or "growing" in q:
        return PICKLEBALL_KB["general"]["popularity"]

    # ---- Rules ----
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

    # ---- Equipment (placed after players so 'pickleball player' doesn't hit 'ball') ----
    if "paddle" in q:
        return PICKLEBALL_KB["equipment"]["paddle"]
    if "ball" in q:
        return PICKLEBALL_KB["equipment"]["ball"]
    if "court" in q or "dimension" in q or "size" in q:
        return PICKLEBALL_KB["equipment"]["court"]

    # ---- Fallback: try key name matches anywhere ----
    for section, items in PICKLEBALL_KB.items():
        for key, text in items.items():
            if key in q:
                return text

    return "No exact fact found in the knowledge base; answer from general understanding."
def pickleball_agent(question: str) -> str:
    kb_info = search_kb(question)

    system_prompt = (
        "You are a friendly pickleball FAQ assistant. "
        "Use the provided knowledge base info when helpful, but you can also explain in your own words. "
        "Be clear and concise; talk to a beginner."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User question: {question}\n\nKB info: {kb_info}"},
    ]

    answer = call_openrouter_api(messages, temperature=0.5)

    # If online model failed, fall back to KB text directly
    if isinstance(answer, str) and "online model failed" in answer:
        return kb_info

    return answer

