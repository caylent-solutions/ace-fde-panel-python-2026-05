from app.services.notifications.templates import TEMPLATES


def load_template(template_key: str) -> str:
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")
    return TEMPLATES[template_key]


def render_template(template_key: str, context: dict) -> str:
    template = load_template(template_key)
    return template.format(**context)
