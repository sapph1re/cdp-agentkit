from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext
import cdp_agentkit_core.actions.social.twitter.context as context
from cdp_agentkit_core.actions.social.twitter.mentions_monitor_start import threads

MENTIONS_MONITOR_STOP_PROMPT = """
Stop monitoring twitter mentions.
"""

class MentionsMonitorStopInput(BaseModel):
    pass

def mentions_monitor_stop() -> str:
    print("hmm?")
    #  print(context.unwrap().get("test"))
    #  print(context.unwrap().mentions.get())
    #  print(context.thread.get())

    #  print(get_thread())
    #  print(get_thread().running)
    #  get_thread().stop()
    #  print(get_thread().running)

    print(threads.qsize())
    thread = threads.get()
    print(thread.running)
    thread.stop()
    print(thread.running)

    #  context.set("mentions-monitor-state", "stopped")

    return "stopping monitoring..."

class MentionsMonitorStopAction(TwitterAction):
    name: str = "mentions_monitor_stop"
    description: str = MENTIONS_MONITOR_STOP_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStopInput
    func: Callable[..., str] = mentions_monitor_stop
