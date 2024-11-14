from cdp_agentkit_core.actions.social.twitter.action import (
    Action as TwitterAction,
    ActionThread as TwitterActionThread,
)
from cdp_agentkit_core.actions.social.twitter.context import TwitterContext as TwitterContext

from cdp_agentkit_core.actions.social.twitter.account_details import AccountDetailsAction
from cdp_agentkit_core.actions.social.twitter.mentions_monitor_details import (
    MentionsMonitorDetailsAction,
)
from cdp_agentkit_core.actions.social.twitter.mentions_monitor_start import (
    MentionsMonitorStartAction,
)
from cdp_agentkit_core.actions.social.twitter.mentions_monitor_stop import MentionsMonitorStopAction
from cdp_agentkit_core.actions.social.twitter.mentions_responder_details import (
    MentionsResponderDetailsAction,
)
from cdp_agentkit_core.actions.social.twitter.mentions_responder_start import (
    MentionsResponderStartAction,
)
from cdp_agentkit_core.actions.social.twitter.mentions_responder_stop import (
    MentionsResponderStopAction,
)
from cdp_agentkit_core.actions.social.twitter.post_tweet import PostTweetAction


def get_all_twitter_actions() -> list[type[TwitterAction]]:
    actions = []
    for action in TwitterAction.__subclasses__():
        actions.append(action())

    return actions


TWITTER_ACTIONS = get_all_twitter_actions()

__all__ = [
    "TwitterAction",
    "TwitterActionThread",
    "TwitterContext",
    "AccountDetailsAction",
    "MentionsMonitorDetailsAction",
    "MentionsMonitorStartAction",
    "MentionsMonitorStopAction",
    "MentionsResponderDetailsAction",
    "MentionsResponderStartAction",
    "MentionsResponderStopAction",
    "PostTweetAction",
    "TWITTER_ACTIONS",
]
