def run_agent(question: str) -> str:
    q = question.strip().lower()

    # If it's just a greeting, answer directly without KB
    if q in {"hi", "hello", "hey", "hii", "hai"} or q.startswith(("hi ", "hello ", "hey ")):
        return (
            "Hi! Great to see you here. 👋\n"
            "Ask me anything about sports rules, training tips, equipment, or famous players, "
            "and I’ll break it down for you."
        )

    # For real questions, build a fallback KB answer
    fallback_answer = sports_kb_tool.run(question)

    if not OPENROUTER_API_KEY:
        return fallback_answer

    llm = build_llm()

    system_text = (
        "You are a super friendly, energetic multi-sport coach with internet access. "
        "Use your own knowledge and any available tools (like web browsing) to answer "
        "questions about any sport as accurately and up to date as possible. "
        "Be conversational and explain in simple language."
    )

    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=question),
    ]

    try:
        resp = llm.invoke(messages)
        return resp.content
    except Exception:
        return fallback_answer
