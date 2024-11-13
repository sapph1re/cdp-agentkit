#  from contextvars import ContextVar

#  import tweepy

#  api: ContextVar[tweepy.API] = ContextVar("api", default=None)
#  client: ContextVar[tweepy.Client] = ContextVar("client", default=None)

#  def get_api() -> tweepy.API:
#      return api.get()

#  def set_api(value: tweepy.API):
#      api.set(value)

#  def get_client() -> tweepy.Client:
#      return client.get()

#  def set_client(value: tweepy.Client):
#      client.set(value)

from contextvars import ContextVar
from contextlib import contextmanager

import tweepy

from cdp_agentkit_core.actions.context import Context


class TwitterContext(Context):
    mentions = ContextVar("mentions", default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = ContextVar("client", default=None)
        #  self.mentions = ContextVar("mentions", default=None)

    def get_client(self) -> tweepy.Client:
        return self._client.get()

    def set_client(self, value: tweepy.Client):
        self._client.set(value)

#  context: TwitterContext = TwitterContext()

#  def current() -> TwitterContext:
#      inst = _context.get()
#      if inst is None:
#          raise Runtimeerror("TwitterContext not found")

#      return inst

#  def new() -> TwitterContext:


#  def get_context() -> TwitterContext:
#      return _context.get()

#  def set_context(ctx:TwitterContext):
#      _context.set(ctx)

def unwrap() ->TwitterContext:
    return _context.get()

def get_client() -> tweepy.Client:
    return _context.get().get_client()

def set_client(client: tweepy.Client):
    _context.get().set_client(client)


@contextmanager
def current():
    ctx = _context.get()

    if ctx is None:
        raise Runtimeerror("TwitterContext not found")

    try:
        yield ctx
    finally:
        pass

@contextmanager
def new():
    ctx = TwitterContext()
    token = _context.set(ctx)
    try:
        yield ctx
    finally:
        _context.reset(token)

_context = ContextVar('twitter_context', default=None)
_context.set(TwitterContext())

thread = ContextVar('twitter_threads', default=None)
