def get_stage(messages):
    if not messages:
        return "early"

    text = " ".join([m["content"].lower() for m in messages])

    scores = {
        "considering": 0,
        "hesitant": 0,
        "pain": 0,
        "early": 1,  # default bias
    }

    # Close/considering signals
    for kw in ["price", "cost", "how much", "invest", "afford", "payment", "pay", "fee", "charge", "worth it"]:
        if kw in text:
            scores["considering"] += 2

    # Hesitant signals
    for kw in ["not sure", "thinking about it", "maybe", "idk", "i don't know", "need to think",
                "not for me", "skeptical", "scared", "nervous", "worried", "risky"]:
        if kw in text:
            scores["hesitant"] += 2

    # Pain/interested signals
    for kw in ["struggling", "problem", "issue", "failing", "can't", "stuck", "frustrated",
                "tried", "doesn't work", "not working", "help", "need", "want", "goal", "dream"]:
        if kw in text:
            scores["pain"] += 1

    return max(scores, key=scores.get)


def get_instruction(stage):
    instructions = {
        "early": (
            "They just started. Warm them up. Ask a single open-ended question "
            "to understand their situation. Do NOT pitch or mention the offer yet."
        ),
        "pain": (
            "They've shared a struggle. Dig deeper — make them feel genuinely understood. "
            "Mirror their words back. Ask what they've tried. Still no pitch yet."
        ),
        "hesitant": (
            "They're on the fence. Acknowledge their hesitation, normalize it, "
            "then ask one specific question to uncover the real blocker. "
            "Use the objection handles from the persona context if relevant."
        ),
        "considering": (
            "They're interested and thinking about cost or next steps. "
            "Be confident. Don't over-explain. Guide them to book a call using the booking link from the persona context."
        ),
    }
    return instructions.get(stage, "Be genuinely helpful.")
