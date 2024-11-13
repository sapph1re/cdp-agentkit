from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext
from cdp_agentkit_core.actions.social.twitter.context import context
from cdp_agentkit_core.actions.social.twitter.mentions_monitor_start import threads

MENTIONS_MONITOR_STOP_PROMPT = """
Stop monitoring twitter mentions.
"""

class MentionsMonitorStopInput(BaseModel):
    pass

def mentions_monitor_stop() -> str:
    print("mentions monitor stop action")
    #  print(context.unwrap().get("test"))
    #  print(context.unwrap().mentions.get())
    #  print(context.thread.get())

    #  print(get_thread())
    #  print(get_thread().running)
    #  get_thread().stop()
    #  print(get_thread().running)

    #  print(context.thread.get())

    #  print(threads.qsize())
    #  thread = threads.get()

    ctx = context()
    thread = ctx.get("monitor-thread")

    if thread is None:
        return "monitor cannot be stopped, it is not running!"

    print(thread.running)
    thread.stop()
    print(thread.running)

    ctx.set("monitor-thread", None)

    #  context.set("mentions-monitor-state", "stopped")

    return "stopping monitoring..."

class MentionsMonitorStopAction(TwitterAction):
    name: str = "mentions_monitor_stop"
    description: str = MENTIONS_MONITOR_STOP_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStopInput
    func: Callable[..., str] = mentions_monitor_stop
