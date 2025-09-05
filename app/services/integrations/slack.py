from .base import IntegrationHandler

SLACK_TIMEOUT = 5


class SlackIntegration(IntegrationHandler):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send(self, payload):
        url = self.webhook_url
        # TODO: actually call slack
        print("would post to", url, payload)
