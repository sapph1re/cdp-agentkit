"""Util that calls Twitter API."""

from collections.abc import Callable
from typing import Any

#  from contextvars_registry import ContextVarsRegistry
from cdp_agentkit_core.actions.social.twitter import TwitterContext
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, model_validator
import tweepy

#  class TwitterContext(ContextVarsRegistry):
#      client: tweepy.Client | None = None


class TwitterApiWrapper(BaseModel):
    """Wrapper for Twitter API."""

    context: TwitterContext | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: dict) -> Any:
        """Validate that Twitter access token, token secret, and tweepy exists in the environment."""
        api_key = get_from_dict_or_env(values, "twitter_api_key", "TWITTER_API_KEY")
        api_secret = get_from_dict_or_env(values, "twitter_api_secret", "TWITTER_API_SECRET")
        access_token = get_from_dict_or_env(values, "twitter_access_token", "TWITTER_ACCESS_TOKEN")
        access_token_secret = get_from_dict_or_env(values, "twitter_access_token_secret", "TWITTER_ACCESS_TOKEN_SECRET")

        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        context = TwitterContext()
        context.set_client(client)

        values["context"] = context
        values["client"] = context.client
        values["api_key"] = api_key
        values["api_secret"] = api_secret
        values["access_token"] = access_token
        values["access_token_secret"] = access_token_secret

        return values

    def run_action(self, func: Callable[..., str], **kwargs) -> str:
        """Run a Twitter Action."""

        #  func_signature = inspect.signature(func)
        #  first_kwarg = next(iter(func_signature.parameters.values()), None)

        return func(self.context, **kwargs)

        #  if first_kwarg and first_kwarg.annotation is tweepy.Client:
        #      return func(self.client, **kwargs)
        #  else:
        #      return func(**kwargs)
