from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext

MENTIONS_MONITOR_DETAILS_PROMPT = """
"""

class MentionsMonitorDetailsInput(BaseModel):
    pass

def mentions_monitor_details(context: TwitterContext) -> str:
    pass

class MentionsMonitorDetailsAction(TwitterAction):
    name: str = "mentions_monitor_details"
    description: str = MENTIONS_MONITOR_DETAILS_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorDetailsInput
    func: Callable[..., str] = mentions_monitor_details
