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
from pydantic import Field


#  _context = ContextVar('twitter_context', default=None)

class TwitterContext(Context):
    class Config:
        arbitrary_types_allowed = True

    client:ContextVar[tweepy.Client] = ContextVar("client", default=None)

    #  = ContextVar("client", default=None)

    #  def __init__(self, *args, **kwargs):
    #      super().__init__(*args, **kwargs)
        #  self._mentions = ContextVar("mentions", default=None)
        #  self.mentions = ContextVar("mentions", default=None)

    #  def get_client(self) -> tweepy.Client:
    #      return self.get("client")
    #      #  return self._client.get()

    #  def set_client(self, value: tweepy.Client):
    #      return self.set("client", value)
    #      #  self._client.set(value)

    #  def get_mentions(self) -> any:
    #      return self._mentions.get()

    #  def set_mentions(self, value: any):
    #      self._mentions.set(value)

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

#  def unwrap() ->TwitterContext:
#      return _context.get()

#  def get_client() -> tweepy.Client:
#      return _context.get().get_client()

#  def set_client(client: tweepy.Client):
#      _context.get().set_client(client)

#  def get_mentions() -> any:
#      return _context.get().get_mentions()

#  def set_mentions(mentions: any):
#      _context.get().set_mentions(mentions)


def context() -> TwitterContext:
    return _context.get()

@contextmanager
def current():
    ctx = _context.get()

    if ctx is None:
        raise RuntimeError("TwitterContext not found")

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

#  thread = ContextVar('twitter_threads', default=None)
