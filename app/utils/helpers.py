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


def normalize_phone(phone):
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    return digits


def is_uuid(val):
    if not val:
        return False
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, str(val).lower()))


def coerce_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, (str, int, float, bool)):
        return [val]
    try:
        return list(val)
    except TypeError:
        return [val]


def strip_whitespace_keys(d):
    return {k.strip(): v for k, v in d.items()}


def remove_none_values(d):
    return {k: v for k, v in d.items() if v is not None}


def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunk_string(s, size):
    return [s[i:i+size] for i in range(0, len(s), size)]


def pad_left(s, width, char="0"):
    return str(s).rjust(width, char)


def pad_right(s, width, char=" "):
    return str(s).ljust(width, char)


def cents_to_dollars(cents):
    return round(cents / 100, 2)


def dollars_to_cents(dollars):
    return int(round(dollars * 100))


def format_currency(amount_cents, symbol="$"):
    dollars = cents_to_dollars(amount_cents)
    return f"{symbol}{dollars:,.2f}"


def parse_key_value_string(s, pair_sep=",", kv_sep="="):
    result = {}
    for pair in s.split(pair_sep):
        pair = pair.strip()
        if kv_sep in pair:
            k, v = pair.split(kv_sep, 1)
            result[k.strip()] = v.strip()
    return result


def build_query_string(params):
    parts = []
    for k, v in params.items():
        if v is None:
            continue
        parts.append(f"{k}={v}")
    return "&".join(parts)


def parse_bool_string(s):
    if not s:
        return False
    return str(s).lower() in ("1", "true", "yes", "on", "enabled")


def get_nested(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def set_nested(d, keys, value):
    cur = d
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    cur[keys[-1]] = value
    return d


def invert_dict(d):
    return {v: k for k, v in d.items()}


def count_by(lst, key_fn):
    counts = {}
    for item in lst:
        k = key_fn(item)
        counts[k] = counts.get(k, 0) + 1
    return counts


def zip_to_dict(keys, values):
    return dict(zip(keys, values))


def rotate_list(lst, n):
    if not lst:
        return lst
    n = n % len(lst)
    return lst[n:] + lst[:n]


def moving_average(lst, window):
    result = []
    for i in range(len(lst)):
        start = max(0, i - window + 1)
        window_vals = lst[start:i+1]
        result.append(sum(window_vals) / len(window_vals))
    return result


def percentile(lst, p):
    if not lst:
        return None
    sorted_lst = sorted(lst)
    idx = int(len(sorted_lst) * p / 100)
    idx = clamp(idx, 0, len(sorted_lst) - 1)
    return sorted_lst[idx]


def weighted_average(values, weights):
    total_weight = sum(weights)
    if total_weight == 0:
        return 0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def is_numeric(val):
    try:
        float(val)
        return True
    except (TypeError, ValueError):
        return False


def snake_to_title(name):
    return " ".join(p.capitalize() for p in name.split("_"))


def title_to_snake(name):
    return "_".join(name.lower().split())


def abbreviate(text, max_words=3):
    words = text.split()
    return "".join(w[0].upper() for w in words[:max_words])


def pluralize(word, count, plural=None):
    if count == 1:
        return word
    if plural:
        return plural
    if word.endswith("y"):
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def iso_now():
    import datetime
    return datetime.datetime.utcnow().isoformat() + "Z"


def unix_now():
    return int(time.time())


def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def human_filesize(size_bytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(c1 != c2)))
        prev = curr
    return prev[len(s2)]


def word_count(text):
    if not text:
        return 0
    return len(text.split())


def sentence_count(text):
    if not text:
        return 0
    return len(re.findall(r"[.!?]+", text))


def extract_emails(text):
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)


def extract_urls(text):
    return re.findall(r"https?://[^\s]+", text)


def hash_string(s, algorithm="sha256"):
    import hashlib
    h = hashlib.new(algorithm)
    h.update(s.encode("utf-8"))
    return h.hexdigest()


def constant_time_compare(a, b):
    import hmac
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def encode_base62(num):
    chars = string.digits + string.ascii_letters
    result = []
    while num:
        result.append(chars[num % 62])
        num //= 62
    return "".join(reversed(result)) or "0"


def decode_base62(s):
    chars = string.digits + string.ascii_letters
    result = 0
    for c in s:
        result = result * 62 + chars.index(c)
    return result


def batch_process(items, fn, batch_size=50):
    results = []
    for batch in chunked(list(items), batch_size):
        results.extend(fn(batch))
    return results


def dedupe_by(lst, key_fn):
    seen = set()
    result = []
    for item in lst:
        k = key_fn(item)
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def find_first(lst, predicate):
    for item in lst:
        if predicate(item):
            return item
    return None


def find_all(lst, predicate):
    return [item for item in lst if predicate(item)]


def index_by(lst, key_fn):
    return {key_fn(item): item for item in lst}


def sum_by(lst, key_fn):
    return sum(key_fn(item) for item in lst)


def max_by(lst, key_fn):
    if not lst:
        return None
    return max(lst, key=key_fn)


def min_by(lst, key_fn):
    if not lst:
        return None
    return min(lst, key=key_fn)


def sliding_window(lst, size):
    for i in range(len(lst) - size + 1):
        yield lst[i:i + size]


def interleave(*lists):
    iters = [iter(l) for l in lists]
    while iters:
        next_iters = []
        for it in iters:
            try:
                yield next(it)
                next_iters.append(it)
            except StopIteration:
                pass
        iters = next_iters


def stringify_keys(d):
    return {str(k): v for k, v in d.items()}


def intify_keys(d):
    result = {}
    for k, v in d.items():
        try:
            result[int(k)] = v
        except (ValueError, TypeError):
            result[k] = v
    return result


def tree_to_flat(tree, parent_key="", sep="."):
    items = {}
    for k, v in tree.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(tree_to_flat(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def flat_to_tree(flat, sep="."):
    result = {}
    for key, val in flat.items():
        parts = key.split(sep)
        set_nested(result, parts, val)
    return result


def memoize(fn):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper


def retry(fn, times=3):
    for i in range(times):
        try:
            return fn()
        except Exception:
            if i == times - 1:
                raise
