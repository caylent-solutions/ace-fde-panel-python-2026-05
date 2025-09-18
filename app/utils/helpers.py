import re
import time
import random
import string


EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def ensure_iso_date(val):
    if isinstance(val, str):
        val = val.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            return val
        if re.match(r"^\d{2}/\d{2}/\d{4}$", val):
            parts = val.split("/")
            return f"{parts[2]}-{parts[0]}-{parts[1]}"
        if re.match(r"^\d{8}$", val):
            return f"{val[:4]}-{val[4:6]}-{val[6:]}"
    return str(val)


def normalize_email(email):
    if not email:
        return ""
    email = email.strip().lower()
    if not re.match(EMAIL_REGEX, email):
        return email
    local, domain = email.split("@", 1)
    local = local.split("+")[0]
    return f"{local}@{domain}"


def is_valid_email(email):
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))


def random_string(length=16):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def truncate(text, max_len=100, suffix="..."):
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("1", "true", "yes", "on")
    return bool(val)


def flatten(lst):
    out = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
