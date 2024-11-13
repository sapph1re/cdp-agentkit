from collections.abc import Callable

import asyncio
import tweepy
from pydantic import BaseModel

from cdp_agentkit_core.actions.social.twitter import TwitterAction, TwitterContext

MENTIONS_MONITOR_START_PROMPT = """
This tool will monitor mentions for the currently authenticated Twitter (X) user context."""

# TODO: enums

class MentionsMonitorStartInput(BaseModel):
    pass


def mentions_monitor_start(context: TwitterContext) -> str:
    try:
        state = context.get("mentions-state")
        if state == "running":
            return "already running"
    except KeyError as e:
        pass

    context.set("mentions-state", "running")
    task = asyncio.create_task(monitor_mentions(context))
    context.set("mentions-task", task)

    return "started monitoring"

def monitor_mentions(context: TwitterContext):
    last_id = 0

    
    try:
        response = context.get_client().get_me()
        me = response.data
    except tweepy.errors.TweepyException as e:
        return f"Error retrieving authenticated user account details: {e}"

    while context.get("mentions-state") == "running":
        try:
            #  mentions = context.get_api().mentions_timeline(since_id=last_id)
            mentions = context.get_client().get_users_mentions(me.id, since_id=last_id)
            for mention in mentions:
                print(f"@{mention.user.screen_name}: {mention.text}")
                last_id = mention.id

        except tweepy.errors.TweepyException as e:
            print(f"Error: {e}")
            return

        asyncio.sleep(60)

class MentionsMonitorStartAction(TwitterAction):
    name: str = "mentions_monitor_start"
    description: str = MENTIONS_MONITOR_START_PROMPT
    args_schema: type[BaseModel] | None = MentionsMonitorStartInput
    func: Callable[..., str] = mentions_monitor_start
