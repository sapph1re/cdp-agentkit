from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext

MENTIONS_MONITOR_START_PROMPT = """
"""

class MentionsMonitorStartInput(BaseModel):
    pass

def mentions_monitor_start(context: TwitterContext) -> str:
    pass

class MentionsMonitorStartAction(TwitterAction):
    name: str = "mentions_monitor_start"
    description: str = MENTIONS_MONITOR_START_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStartInput
    func: Callable[..., str] = mentions_monitor_start
