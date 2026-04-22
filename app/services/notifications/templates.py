TEMPLATES: dict[str, str] = {
    "run_complete": "Your run '{run_name}' has completed.",
    "run_failed": "Your run '{run_name}' failed. Check the logs for details.",
    "welcome": "Welcome to Cadence, {username}!",
}


def render(template_key, context):
    from app.services.notifications.loader import render_template
    return render_template(template_key, context)
