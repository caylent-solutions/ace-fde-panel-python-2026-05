from app.services.integrations.slack import SlackIntegration
from app.services.integrations.github import GitHubIntegration


def test_slack_has_webhook_url():
    s = SlackIntegration(webhook_url="https://hooks.slack.com/test")
    assert s.webhook_url == "https://hooks.slack.com/test"


def test_github_has_repo():
    g = GitHubIntegration(token="tok", repo="org/repo")
    assert g.repo == "org/repo"
