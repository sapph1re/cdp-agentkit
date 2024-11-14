from collections.abc import Callable
from queue import Queue
import contextvars
import time
import threading

import tweepy

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import (
    TwitterAction,
    TwitterActionThread,
    TwitterContext,
)

from cdp_agentkit_core.actions.social.twitter.context import context

MENTIONS_MONITOR_START_PROMPT = """
This tool will monitor mentions for the currently authenticated Twitter (X) user context."""


class MentionsMonitorStartInput(BaseModel):
    pass


def mentions_monitor_start() -> str:
    thread = MonitorMentionsThread()

    ctx = context()
    ctx.set("monitor-thread", thread)

    thread.start()

    return "Successfully started monitoring for Twitter (X) mentions."


class MonitorMentionsThread(TwitterActionThread):

    """
    https://developer.x.com/en/docs/x-api/rate-limits
    """
    backoff: list[int] = [2, 60, 15*60]

    """
    current position within the backoff list
    """
    backoff_index: int

    ""
    errors: Queue = Queue()
    ""

    """
    ammount of time waited since the last successful call.
    """
    waited: int

    """
    last mention id retrieved
    """
    mention_id: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fn = self.monitor

    def monitor(self):
        ctx = context()
        client = ctx.client.get()

        if client is None:
            raise RuntimeError("Twitter (X) client is unavailable.")

        try:
            response = client.get_me()
            me = response.data
        except tweepy.errors.TweepyException as e:
            raise RuntimeError("Twitter (X) client is unavailable.")

        self.running = True

        while self.running:
            waited += 1

            if waited < self.backoff[self.backoff_index]:
                time.sleep(1)
                continue

            try:
                response = client.get_users_mentions(me.id, since_id=self.mention_id)
                mentions = response.data
            except tweepy.errors.TweepyException as e:
                raise e
                self.errors.put(e)
                self.backoff_index = min(self.backoff_index + 1, len(self.backoff) - 1)

                if self.backoff[self.backoff_index] > waited:
                    waited = 0

                continue

            self.process(mentions)
            self.waited = 0

        self.stopped()

    def process(self, mentions):
        collection = context.mentions.get()

        for mention in mentions:
            if mention is None:
                continue

            collection.append(mention)

        self.mention_id = mention.id

        #  while True:
        #  state = context.get("mentions-monitor-state")
        #  if state == "stopped":
        #      break

        # context.get("mentions-state") != "stopped":
        #  try:
        #      print("fetching mentions")

        #      response = context.get_client().get_users_mentions(me.id, since_id=self.mention_id)
        #      mentions = response.data

        #      for mention in mentions:
        #          if mention is None:
        #              print("mention is empty")
        #              continue

        #          print(f"@{mention.user.screen_name}: {mention.text}")
        #          self.mention_id = mention.id

        #  except tweepy.errors.TweepyException as e:
        #      print(f"Error: {e}")

        #  time.sleep(15 * 60)


class MentionsMonitorStartAction(TwitterAction):
    name: str = "mentions_monitor_start"
    description: str = MENTIONS_MONITOR_START_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStartInput
    func: Callable[..., str] = mentions_monitor_start

#  def get_thread() -> MonitorMentionsThread:
#      return _thread.get()

#  def set_thread(t:MonitorMentionsThread):
#      _thread.set(t)

#  threadd: contextvars.ContextVar[MonitorMentionsThread] = contextvars.ContextVar('monitor-mentions-thread', default=None)
