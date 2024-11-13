from collections.abc import Callable
from queue import Queue
import contextvars
import time
import threading

#  import asyncio
import tweepy

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext
import cdp_agentkit_core.actions.social.twitter.context as context
from cdp_agentkit_core.actions.social.twitter.mentions import items

MENTIONS_MONITOR_START_PROMPT = """
This tool will monitor mentions for the currently authenticated Twitter (X) user context."""

# TODO: enums

class MentionsMonitorStartInput(BaseModel):
    pass

def mentions_monitor_start() -> str:
    global trd
    #  try:
    #      state = context.get("mentions-state")
    #      if state == "running":
    #          return "already running"
    #  except KeyError as e:
    #      pass

    #  print(context.get_client())

    #  context.client.set(twitterContext.get_client())
    
    ctx = contextvars.copy_context()
    thread = MonitorMentionsThread(ctx)
    context.unwrap().mentions.set(thread)
    #  context.unwrap().set("test", thread)
    context.thread.set(thread)
    set_thread(thread)
    #  thread._ctx = ctx
    threads.put(thread)
    thread.start()

    print("...")
    #  print(context.unwrap())
    #  print(context.unwrap().mentions.get())
    #  print(context.unwrap().get("test"))
    #  print(context.thread.get())
    print(get_thread())


    #  threadContext = contextvars.copy_context()
    #  threadContext.run(
    #  thread = threading.Thread(target=monitor_mentions, args=(context, ))
    #  thread.start()
    #  context.set("mentions-state", "running")


    #  asyncio.set_event_loop(loop)
    #  task = asyncio.create_task(monitor_mentions(context))
    #  task = asyncio.ensure_future(monitor_mentions(context))
    #  context.set("mentions-task", task)

    #  asyncio.to_thread(monitor_mentions)

    return "started monitoring"

class MonitorMentionsThread(threading.Thread):
    running: bool

    def __init__(self, ctx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ctx = ctx
        #  self._ctx = context._context


        #  print("inbound")
        #  print(.get_client())

        #  self.context = contextvars.copy_context()
        self.mention_id = 0

    def run(self):
        for var, value in self._ctx.items():
            var.set(value)

        print("CONTEXT")
        #  print(self._ctx.get_client())
        print(context.get_client())

        items.put("hi")
        #  return
        #  try:
        #      state = context.get("mentions-monitor-state")
        #      if state == "running":
        #          return
        #  except KeyError as e:
        #      pass

        #  context.set("mentions-monitor-state", "")
        self.running = True
        self.monitor()
        #  context.set("mentions-monitor-state", "running")

    def stop(self):
        self.running = False

    def monitor(self):

        #  try:
        #      response = context.get_client().get_me()
        #      me = response.data
        #      print(me.id)
        #  except tweepy.errors.TweepyException as e:
        #      self.running = False
        #      return f"Error retrieving authenticated user account details: {e}"

        while self.running:
            time.sleep(1)
        #  while True:
            #  state = context.get("mentions-monitor-state")
            #  if state == "stopped":
            #      break

            #context.get("mentions-state") != "stopped":
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

        print("monitoring stopped")

class MentionsMonitorStartAction(TwitterAction):
    name: str = "mentions_monitor_start"
    description: str = MENTIONS_MONITOR_START_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStartInput
    func: Callable[..., str] = mentions_monitor_start

def get_thread() -> MonitorMentionsThread:
    return _thread.get()

def set_thread(t:MonitorMentionsThread):
    _thread.set(t)

_thread: contextvars.ContextVar[MonitorMentionsThread] = contextvars.ContextVar('monitor-mentions-thread', default=None)

threads = Queue()
