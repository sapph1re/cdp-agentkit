import contextvars

import tweepy

from cdp_agentkit_core.actions.context import Context


class Context(Context):
    client: contextvars.ContextVar[tweepy.Client] | None = None

    def __init__(self):
        super().__init__()
        self.client = contextvars.ContextVar("client", default=None)

    def get_client(self) -> tweepy.Client:
        return self.client.get()

    def set_client(self, value: tweepy.Client):
        self.client.set(value)

