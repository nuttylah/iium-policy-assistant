
import re


def extract_query_constraints(query: str) -> dict:
    """Extract metadata and policy constraints from a user query."""

    query_lower = query.lower()

    # Nationality
    if "international" in query_lower:
        nationality = "International"
    elif "malaysian" in query_lower:
        nationality = "Malaysian"
    else:
        nationality = None

    # Study level
    if "undergraduate" in query_lower:
        level = "Undergraduate"
    elif "master" in query_lower:
        level = "Master"
    else:
        level = None

    # Kulliyyah
    # Check longer or more specific keywords before shorter ones.
    kulliyyah_keywords = {
        "ahas kirkhs": "AHAS KIRKHS",
        "kirkhs": "AHAS KIRKHS",
        "medicine": "KOM",
        "dentistry": "KOD",
        "pharmacy": "KOP",
        "nursing": "KON",
        "engineering": "KOE",
        "education": "KOED",
        "science": "KOS",
        "aikol": "AIKOL",
        "kenms": "KENMS",
        "kstcl": "KSTCL",
        "celpad": "CELPAD",
        "kaed": "KAED",
        "kahs": "KAHS",
        "kict": "KICT",
        "koed": "KOED",
        "koe": "KOE",
        "kos": "KOS",
        "kop": "KOP",
        "kom": "KOM",
        "kod": "KOD",
        "kon": "KON",
    }

    kulliyyah = None

    for keyword, value in kulliyyah_keywords.items():
        if keyword in query_lower:
            kulliyyah = value
            break

    # ODL is a learning mode, not a Kulliyyah.
    learning_mode = "ODL" if re.search(
        r"\bodl\b|open and distance learning", query_lower
    ) else None

    # Policy intent
    if any(
        keyword in query_lower
        for keyword in (
            "withdraw",
            "withdrawal",
            "study leave",
            "refund",
            "refunded",
            "refunds",
        )
    ):
        intent = "Withdrawal/Refund"

    elif any(
        keyword in query_lower
        for keyword in (
            "entrance fee",
            "entrance fees",
            "application fee",
            "non-refundable",
        )
    ):
        intent = "Entrance Fee"

    elif any(
        keyword in query_lower
        for keyword in (
            "tuition fee",
            "tuition fees",
            "total fee",
            "total fees",
            "fee",
            "fees",
            "cost",
        )
    ):
        intent = "Tuition Fee"

    else:
        intent = None

    # Policy condition
    if "first month" in query_lower:
        condition = "First Month"
    elif "second month" in query_lower:
        condition = "Second Month"
    elif "first day" in query_lower:
        condition = "First Day"
    else:
        condition = None

    return {
        "nationality": nationality,
        "level": level,
        "kulliyyah": kulliyyah,
        "learning_mode": learning_mode,
        "intent": intent,
        "condition": condition,
    }


def metadata_match_score(result: dict, constraints: dict) -> int:
    """Score a retrieved chunk against query metadata and policy intent."""

    metadata = result["metadata"]
    text = result["text"].lower()
    score = 0

    # Metadata matches
    for field in ("nationality", "level", "kulliyyah"):
        expected = constraints.get(field)

        if expected is not None and metadata.get(field) == expected:
            score += 1

    # Policy intent
    if constraints.get("intent") == "Withdrawal/Refund":
        if re.search(
            r"\bwithdraw(?:al|n|ing)?\b|\bstudy leave\b|\brefund(?:ed|s)?\b",
            text,
        ):
            score += 2

    elif constraints.get("intent") == "Entrance Fee":
        if any(
            phrase in text
            for phrase in (
                "entrance fee",
                "entrance fees",
                "application fee",
                "non-refundable",
            )
        ):
            score += 2

    elif constraints.get("intent") == "Tuition Fee":
        if any(
            phrase in text
            for phrase in ("tuition", "total fee", "total fees")
        ):
            score += 1

    # Policy condition and percentage must be supported by the same chunk.
    condition = constraints.get("condition")

    if constraints.get("intent") == "Withdrawal/Refund":
        has_refund = "refund" in text

        if condition == "First Month":
            if "first month" in text and has_refund:
                score += 2
            if (
                "first month" in text
                and "90%" in text
                and "refund" in text
            ):
                score += 2

        elif condition == "Second Month":
            if "second month" in text and has_refund:
                score += 2
            if (
                "second month" in text
                and "60%" in text
                and "refund" in text
            ):
                score += 2

        elif condition == "First Day":
            if "first day" in text and has_refund:
                score += 2

    return score


def metadata_aware_rank(
    results: list[dict],
    constraints: dict,
) -> list[dict]:
    """Remove conflicting metadata and rank the remaining results."""

    filtered_results = []

    for result in results:
        metadata = result.get("metadata", {})

        # Discard results that conflict with explicit query constraints.
        if any(
            constraints.get(field) is not None
            and metadata.get(field) != constraints[field]
            for field in ("nationality", "level", "kulliyyah")
        ):
            continue

        updated_result = result.copy()
        updated_result["metadata_match_score"] = metadata_match_score(
            result, constraints
        )
        filtered_results.append(updated_result)

    # Metadata score first; cross-encoder score breaks ties.
    filtered_results.sort(
        key=lambda item: (
            item["metadata_match_score"],
            item.get("rerank_score", float("-inf")),
        ),
        reverse=True,
    )

    return filtered_results
