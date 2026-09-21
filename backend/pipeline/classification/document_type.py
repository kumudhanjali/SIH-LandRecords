def classify_document(text):
    text = text.lower()

    keywords = {
        "land_record": [
            "survey number",
            "survey no",
            "land",
            "plot",
            "owner",
            "village"
        ],
        "sale_deed": [
            "sale deed",
            "vendor",
            "purchaser",
            "sale consideration"
        ],
        "property_tax": [
            "property tax",
            "tax assessment",
            "tax receipt"
        ]
    }

    scores = {}

    for document_type, words in keywords.items():
        score = 0

        for word in words:
            if word in text:
                score += 1

        scores[document_type] = score

    if not scores or max(scores.values()) == 0:
        return {
            "document_type": "unknown",
            "confidence": 0.0
        }

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    confidence = best_score / len(keywords[best_type])

    return {
        "document_type": best_type,
        "confidence": round(confidence, 2)
    }