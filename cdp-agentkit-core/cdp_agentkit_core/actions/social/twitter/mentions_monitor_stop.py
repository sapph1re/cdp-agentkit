from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext

MENTIONS_MONITOR_STOP_PROMPT = """
"""

class MentionsMonitorStopInput(BaseModel):
    pass

def mentions_monitor_stop(context: TwitterContext) -> str:
    pass

class MentionsMonitorStopAction(TwitterAction):
    name: str = "mentions_monitor_stop"
    description: str = MENTIONS_MONITOR_STOP_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStopInput
    func: Callable[..., str] = mentions_monitor_stop
