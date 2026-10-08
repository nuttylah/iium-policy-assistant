def extract_query_constraints(query: str) -> dict:
    """
    Extract nationality, study-level, Kulliyyah,
    policy intent, and policy condition constraints
    from the query.
    """

    query_lower = query.lower()

    # ============================================================
    # Detect nationality
    # ============================================================

    if "international" in query_lower:
        nationality = "International"

    elif "malaysian" in query_lower:
        nationality = "Malaysian"

    else:
        nationality = None

    # ============================================================
    # Detect study level
    # ============================================================

    if "undergraduate" in query_lower:
        level = "Undergraduate"

    elif "master" in query_lower:
        level = "Master"

    else:
        level = None

    # ============================================================
    # Detect Kulliyyah
    # ============================================================

    kulliyyah_keywords = {
        "kict": "KICT",
        "aikol": "AIKOL",
        "kenms": "KENMS",
        "ahas kirkhs": "AHAS KIRKHS",
        "kirkhs": "AHAS KIRKHS",
        "koed": "KOED",
        "kstcl": "KSTCL",
        "koe": "KOE",
        "kaed": "KAED",
        "kos": "KOS",
        "kahs": "KAHS",
        "kop": "KOP",
        "kom": "KOM",
        "kod": "KOD",
        "kon": "KON",
        "celpad": "CELPAD",
        "odl": "KON",
        "medicine": "KOM",
        "dentistry": "KOD",
        "pharmacy": "KOP",
        "nursing": "KON",
        "engineering": "KOE",
        "education": "KOED",
        "science": "KOS"
    }

    kulliyyah = None

    for keyword, value in kulliyyah_keywords.items():
        if keyword in query_lower:
            kulliyyah = value
            break

    # ============================================================
    # Detect policy intent
    # ============================================================

    if any(
        keyword in query_lower
        for keyword in [
            "withdraw",
            "withdrawal",
            "study leave",
            "refund",
            "refunded",
            "refunds"
        ]
    ):
        intent = "Withdrawal/Refund"

    elif any(
        keyword in query_lower
        for keyword in [
            "entrance fee",
            "entrance fees",
            "application fee",
            "non-refundable"
        ]
    ):
        intent = "Entrance Fee"

    elif any(
        keyword in query_lower
        for keyword in [
            "tuition fee",
            "tuition fees",
            "total fee",
            "total fees",
            "fee",
            "fees",
            "cost"
        ]
    ):
        intent = "Tuition Fee"

    else:
        intent = None

    # ============================================================
    # Detect policy condition
    # ============================================================

    if "first month" in query_lower:
        condition = "First Month"

    elif "second month" in query_lower:
        condition = "Second Month"

    elif "first day" in query_lower:
        condition = "First Day"

    else:
        condition = None

    # ============================================================
    # Return all constraints
    # ============================================================

    return {
        "nationality": nationality,
        "level": level,
        "kulliyyah": kulliyyah,
        "intent": intent,
        "condition": condition
    }


def metadata_match_score(
    result: dict,
    constraints: dict
) -> int:
    """
    Give a score based on how well the result matches
    the query metadata, policy intent, and policy condition.
    """

    metadata = result["metadata"]
    text = result["text"].lower()

    score = 0

    # ============================================================
    # Match nationality
    # ============================================================

    if (
        constraints["nationality"] is not None
        and metadata["nationality"] == constraints["nationality"]
    ):
        score += 1

    # ============================================================
    # Match study level
    # ============================================================

    if (
        constraints["level"] is not None
        and metadata["level"] == constraints["level"]
    ):
        score += 1

    # ============================================================
    # Match Kulliyyah
    # ============================================================

    if (
        constraints["kulliyyah"] is not None
        and metadata["kulliyyah"] == constraints["kulliyyah"]
    ):
        score += 1

    # ============================================================
    # Match policy intent
    # ============================================================

    if constraints["intent"] == "Withdrawal/Refund":

        withdrawal_keywords = [
            "withdrawal",
            "withdraw",
            "study leave",
            "refunded",
            "refund"
        ]

        if any(keyword in text for keyword in withdrawal_keywords):
            score += 2

    elif constraints["intent"] == "Entrance Fee":

        entrance_keywords = [
            "entrance fee",
            "entrance fees",
            "non-refundable"
        ]

        if any(keyword in text for keyword in entrance_keywords):
            score += 2

    elif constraints["intent"] == "Tuition Fee":

        tuition_keywords = [
            "tuition",
            "tuition fee",
            "tuition fees"
        ]

        if any(keyword in text for keyword in tuition_keywords):
            score += 1

    # ============================================================
    # Match policy condition
    # ============================================================

    if constraints["condition"] == "First Month":

        if (
            "first month" in text
            and "refund" in text
        ):
            score += 2

        if (
            "first month" in text
            and "90%" in text
        ):
            score += 2

    elif constraints["condition"] == "Second Month":

        if (
            "second month" in text
            and "refund" in text
        ):
            score += 2

        if (
            "second month" in text
            and "60%" in text
        ):
            score += 2

    elif constraints["condition"] == "First Day":

        if (
            "first day" in text
            and "refund" in text
        ):
            score += 2

    # ============================================================
    # Return final score
    # ============================================================

    return score


def metadata_aware_rank(
    results: list[dict],
    constraints: dict
) -> list[dict]:
    """
    Rank results based on metadata, policy intent,
    and policy condition matching.
    """

    ranked_results = []

    for result in results:

        updated_result = result.copy()

        updated_result["metadata_match_score"] = metadata_match_score(
            result,
            constraints
        )

        ranked_results.append(updated_result)

    ranked_results.sort(
        key=lambda x: x["metadata_match_score"],
        reverse=True
    )

    return ranked_results