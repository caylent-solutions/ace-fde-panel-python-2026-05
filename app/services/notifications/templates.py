TEMPLATES: dict[str, str] = {
    "run_complete": "Your run '{run_name}' has completed.",
    "run_failed": "Your run '{run_name}' failed. Check the logs for details.",
    "welcome": "Welcome to Cadence, {username}!",
}


def render(template_key: str, context: dict) -> str:
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")
    template = TEMPLATES[template_key]
    return template.format(**context)
