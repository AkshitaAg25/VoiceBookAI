
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import dateparser
from dateparser.search import search_dates


TIMEZONE = ZoneInfo("Asia/Kolkata")


def get_current_time():
    return datetime.now(TIMEZONE)


def find_task(text):
    text = text.lower()

    patterns = {
        "reschedule": r"\b(reschedule|change|move)\b",
        "delete": r"\b(delete|cancel|remove)\b",
        "book": r"\b(book|schedule|reserve)\b",
        "check": r"\b(check|view|find|show)\b",
    }

    matches = []

    for task, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            matches.append((match.start(), task))

    if not matches:
        return None

    # Use the first action mentioned in the sentence.
    return min(matches)[1]


def find_times(text):
    """Extract common time formats such as 8pm and 6:30 PM."""

    pattern = (
        r"\b(?:"
        r"\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)"
        r"|"
        r"\d{1,2}:\d{2}"
        r")\b"
    )

    results = []

    for match in re.finditer(pattern, text, re.IGNORECASE):
        raw = match.group().lower()
        cleaned = re.sub(r"\s+", "", raw)
        cleaned = cleaned.replace(".", "")

        formats = [
            "%I%p",
            "%I:%M%p",
            "%H:%M",
        ]

        parsed = None

        for fmt in formats:
            try:
                parsed = datetime.strptime(cleaned, fmt)
                break
            except ValueError:
                continue

        if parsed:
            results.append({
                "value": parsed.strftime("%H:%M"),
                "start": match.start(),
                "end": match.end()
            })

    return results


def find_dates(text):
    """Extract dates, including tomorrow and 11 October."""

    now = get_current_time()

    found = search_dates(
        text,
        languages=["en"],
        settings={
            "RELATIVE_BASE": now.replace(
                hour=12, minute=0, second=0, microsecond=0
            ),
            "PREFER_DATES_FROM": "future",
            "DATE_ORDER": "DMY",
        }
    )

    if not found:
        return []

    results = []

    for phrase, parsed_date in found:
        phrase_lower = phrase.lower().strip()

        # Ignore matches that are only a time.
        if re.fullmatch(
            r"\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)",
            phrase_lower
        ):
            continue

        # Keep phrases that contain a recognizable date indicator.
        has_date_word = bool(re.search(
            r"\b(today|tomorrow|yesterday|"
            r"monday|tuesday|wednesday|thursday|friday|"
            r"saturday|sunday|"
            r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
            r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
            r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\b",
            phrase_lower
        ))

        has_numeric_date = bool(re.search(
            r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
            phrase_lower
        ))

        if has_date_word or has_numeric_date:
            results.append({
                "value": parsed_date.date().isoformat(),
                "start": text.lower().find(phrase_lower),
                "phrase": phrase
            })

    # Avoid returning the same date more than once.
    unique = []
    seen = set()

    for item in results:
        key = (item["value"], item["start"])

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


def find_name(text):
    """Recognize simple booking requests such as 'for Rahul'."""

    match = re.search(
        r"\bfor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        text
    )

    if not match:
        return None

    name = match.group(1).strip()

    # Avoid mistaking date/time words for a person's name.
    invalid_names = {
        "tomorrow", "today", "yesterday", "monday", "tuesday",
        "wednesday", "thursday", "friday", "saturday", "sunday",
        "next", "the", "an", "a"
    }

    if name.lower() in invalid_names:
        return None

    return name


def extract_appointment_info(firstsen):
    """Return a consistent JSON-compatible dictionary."""

    task = find_task(firstsen)

    if task is None:
        return {
            "status": "missing_info",
            "message": "Would you like to book, delete, reschedule, or check an appointment?",
            "details": None
        }

    dates = find_dates(firstsen)
    times = find_times(firstsen)
    name = find_name(firstsen)

    date_values = [d["value"] for d in dates]
    time_values = [t["value"] for t in times]

    details = {
        "task": task,
        "name": None,
        "date": None,
        "time": None,
        "existing_date": None,
        "existing_time": None,
        "new_date": None,
        "new_time": None
    }

    missing = []

    if task == "book":
        details["name"] = name
        details["date"] = date_values[0] if date_values else None
        details["time"] = time_values[0] if time_values else None

        if not details["name"]:
            missing.append("the person's name")
        if not details["date"]:
            missing.append("the appointment date")
        if not details["time"]:
            missing.append("the appointment time")

    elif task == "delete":
        details["existing_date"] = (
            date_values[0] if date_values else None
        )
        details["existing_time"] = (
            time_values[0] if time_values else None
        )

        if not details["existing_date"]:
            missing.append("the existing appointment date")
        if not details["existing_time"]:
            missing.append("the existing appointment time")

    elif task == "reschedule":
        details["existing_date"] = (
            date_values[0] if len(date_values) > 0 else None
        )
        details["new_date"] = (
            date_values[1] if len(date_values) > 1 else None
        )
        details["existing_time"] = (
            time_values[0] if len(time_values) > 0 else None
        )
        details["new_time"] = (
            time_values[1] if len(time_values) > 1 else None
        )

        if not details["existing_date"]:
            missing.append("the current appointment date")
        if not details["existing_time"]:
            missing.append("the current appointment time")
        if not details["new_date"]:
            missing.append("the new appointment date")
        if not details["new_time"]:
            missing.append("the new appointment time")

    elif task == "check":
        details["date"] = date_values[0] if date_values else None
        details["time"] = time_values[0] if time_values else None

        if not details["date"]:
            missing.append("the appointment date")
        if not details["time"]:
            missing.append("the appointment time")

    if missing:
        question = "Please provide " + ", ".join(missing) + "."
        return {
            "status": "missing_info",
            "message": question,
            "details": details,
            "missing_fields": missing
        }

    return {
        "status": "ready",
        "message": None,
        "details": details
    }


# Test the extractor
if __name__ == "__main__":
    firstsen = "book an appointment for tomorrow at 8pm"

    result = extract_appointment_info(firstsen)

    print(json.dumps(result, indent=4))
