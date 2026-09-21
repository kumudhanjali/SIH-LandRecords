def detect_language(text):
    text = text.strip()

    if not text:
        return {
            "language": "unknown",
            "confidence": 0.0
        }

    # Basic MVP detection using Unicode ranges

    telugu_count = 0
    kannada_count = 0
    hindi_count = 0
    english_count = 0

    for char in text:

        code = ord(char)

        if 0x0C00 <= code <= 0x0C7F:
            telugu_count += 1

        elif 0x0C80 <= code <= 0x0CFF:
            kannada_count += 1

        elif 0x0900 <= code <= 0x097F:
            hindi_count += 1

        elif ("a" <= char.lower() <= "z"):
            english_count += 1

    counts = {
        "Telugu": telugu_count,
        "Kannada": kannada_count,
        "Hindi": hindi_count,
        "English": english_count
    }

    detected_language = max(counts, key=counts.get)
    detected_count = counts[detected_language]

    total = sum(counts.values())

    if total == 0:
        return {
            "language": "unknown",
            "confidence": 0.0
        }

    confidence = detected_count / total

    return {
        "language": detected_language,
        "confidence": round(confidence, 2)
    }