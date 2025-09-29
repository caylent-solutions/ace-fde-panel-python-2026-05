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


def retry_with_backoff(fn, retries=3, base_delay=1.0, exceptions=(Exception,)):
    last_exc = None
    for attempt in range(retries):
        try:
            return fn()
        except exceptions as e:
            last_exc = e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
    raise last_exc


def b64_encode_dict(d):
    import base64
    import json
    raw = json.dumps(d).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def b64_decode_dict(s):
    import base64
    import json
    raw = base64.b64decode(s.encode("utf-8"))
    return json.loads(raw)


def paginate_offset(query, page, page_size=20):
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


def paginate_list(lst, page, page_size=20):
    offset = (page - 1) * page_size
    return lst[offset:offset + page_size]


def deep_merge(base, override):
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def pick(d, keys):
    return {k: d[k] for k in keys if k in d}


def omit(d, keys):
    return {k: v for k, v in d.items() if k not in keys}


def compact(lst):
    return [x for x in lst if x is not None and x != "" and x is not False]


def first_or_none(lst):
    return lst[0] if lst else None


def group_by(lst, key_fn):
    out = {}
    for item in lst:
        k = key_fn(item)
        out.setdefault(k, []).append(item)
    return out


def format_phone_number(phone):
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone


def strip_html_tags(text):
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"&nbsp;", " ", clean)
    clean = re.sub(r"&amp;", "&", clean)
    clean = re.sub(r"&lt;", "<", clean)
    clean = re.sub(r"&gt;", ">", clean)
    return clean.strip()


def camel_to_snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name):
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def mask_string(s, visible=4, char="*"):
    if not s or len(s) <= visible:
        return char * len(s) if s else ""
    return char * (len(s) - visible) + s[-visible:]


def url_join(*parts):
    result = "/".join(p.strip("/") for p in parts if p)
    return result


def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))


def unique(lst):
    seen = set()
    out = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def dict_diff(a, b):
    added = {k: b[k] for k in b if k not in a}
    removed = {k: a[k] for k in a if k not in b}
    changed = {k: (a[k], b[k]) for k in a if k in b and a[k] != b[k]}
    return {"added": added, "removed": removed, "changed": changed}


def split_list(lst, predicate):
    yes, no = [], []
    for item in lst:
        (yes if predicate(item) else no).append(item)
    return yes, no
