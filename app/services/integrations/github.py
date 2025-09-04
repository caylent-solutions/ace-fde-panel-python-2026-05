from .base import IntegrationHandler


class GitHubIntegration(IntegrationHandler):
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo

    def send(self, payload):
        # TODO: actually call github api
        print("would post to github", self.repo, payload)
