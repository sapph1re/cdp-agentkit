from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext
from cdp_agentkit_core.actions.social.twitter.mentions import items

MENTIONS_MONITOR_DETAILS_PROMPT = """show details for mentions."""

class MentionsMonitorDetailsInput(BaseModel):
    pass

def mentions_monitor_details() -> str:
    print(f"size: {items} {items.qsize()}")
    return f"size: {items} {items.qsize()}"
    pass

class MentionsMonitorDetailsAction(TwitterAction):
    name: str = "mentions_monitor_details"
    description: str = MENTIONS_MONITOR_DETAILS_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorDetailsInput
    func: Callable[..., str] = mentions_monitor_details
