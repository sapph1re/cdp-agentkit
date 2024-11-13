from contextvars import ContextVar

import tweepy

from cdp_agentkit_core.actions.context import Context


class Context(Context):
    api: ContextVar[tweepy.API] | None = None
    client: ContextVar[tweepy.Client] | None = None

    def __init__(self):
        super().__init__()
        self.api = ContextVar("api", default=None)
        self.client = ContextVar("client", default=None)

    def get_api(self) -> tweepy.API:
        return self.api.get()

    def set_api(self, value: tweepy.API):
        self.api.set(value)

    def get_client(self) -> tweepy.Client:
        return self.client.get()

    def set_client(self, value: tweepy.Client):
        self.client.set(value)

