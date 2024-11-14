from collections.abc import Callable

from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter.context import context
from cdp_agentkit_core.actions.social.twitter.mentions_monitior import MentionsMonitor

MENTIONS_MONITOR_START_PROMPT = """
This tool will monitor mentions for the currently authenticated Twitter (X) user context."""


class MentionsMonitorStartInput(BaseModel):
    pass


def mentions_monitor_start() -> str:
    monitor = MentionsMonitor()

    ctx = context()
    ctx.set("mentions-monitor", monitor)

    monitor.start()

    return "Successfully started monitoring for Twitter (X) mentions."


class MentionsMonitorStartAction(TwitterAction):
    name: str = "mentions_monitor_start"
    description: str = MENTIONS_MONITOR_START_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStartInput
    func: Callable[..., str] = mentions_monitor_start
