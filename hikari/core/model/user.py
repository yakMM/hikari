#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
"""
Generic users not bound to a guild, and guild-bound member definitions.
"""
from __future__ import annotations

import dataclasses
import datetime
import typing

from hikari.core.model import base
from hikari.core.model import model_cache
from hikari.core.model import presence
from hikari.core.utils import dateutils
from hikari.core.utils import delegate
from hikari.core.utils import transform


@dataclasses.dataclass()
class User(base.Snowflake):
    """
    Representation of a user account.
    """

    __slots__ = ("_state", "id", "username", "discriminator", "avatar_hash", "bot", "__weakref__")

    _state: model_cache.AbstractModelCache

    #: ID of the user.
    #:
    #: :type: :class:`int`
    id: int

    #: The user name.
    #:
    #: :type: :class:`str`
    username: str

    #: The 4-digit discriminator of the object.
    #:
    #: :type: :class:`int`
    discriminator: int

    #: The hash of the user's avatar, or None if they do not have one.
    #:
    #: :type: :class:`str`
    avatar_hash: str

    #: True if the user is a bot, False otherwise
    #:
    #: :type: :class:`bool`
    bot: bool

    def __init__(self, global_state: model_cache.AbstractModelCache, payload):
        self._state = global_state
        self.id = int(payload["id"])
        self.username = payload.get("username")
        self.discriminator = int(payload["discriminator"])
        self.avatar_hash = payload.get("avatar")
        self.bot = payload.get("bot", False)


@delegate.delegate_members(User, "_user")
@dataclasses.dataclass()
class Member(User):
    """
    A specialization of a user which provides implementation details for a specific guild.

    This is a delegate type, meaning it subclasses a :class:`User` and implements it by deferring inherited calls
    and fields to a wrapped user object which is shared with the corresponding member in every guild the user is in.
    """

    __slots__ = ("_user", "_guild_id", "_role_ids", "joined_at", "nick", "premium_since", "presence")

    _user: User
    _role_ids: typing.List[int]
    _guild_id: int

    #: The date and time the member joined this guild.
    #:
    #: :type: :class:`datetime.datetime`
    joined_at: datetime.datetime

    #: The optional nickname of the member.
    #:
    #: :type: :class:`str` or `None`
    nick: typing.Optional[str]

    #: The optional date/time that the member Nitro-boosted the guild.
    #:
    #: :type: :class:`datetime.datetime` or `None`
    premium_since: typing.Optional[datetime.datetime]

    #: The user's online presence.
    #:
    #: :type: :class:`hikari.core.model.presence.Presence`
    presence: presence.Presence

    # noinspection PyMethodOverriding
    def __init__(self, global_state, guild_id, payload):
        self._user = global_state.parse_user(payload["user"])
        self._role_ids = [int(r) for r in payload.get("roles", ())]
        self._guild_id = guild_id
        self.nick = payload.get("nick")
        self.joined_at = dateutils.parse_iso_8601_datetime(payload["joined_at"])
        self.premium_since = transform.nullable_cast(payload.get("premium_since"), dateutils.parse_iso_8601_datetime)
        self.presence = transform.nullable_cast(payload.get("presence"), presence.Presence)

    @property
    def user(self):
        """Returns the internal user object for this member. This is usually only used internally."""
        return self._user


@dataclasses.dataclass()
class BotUser(User):
    """
    A special instance of user to represent the bot that is signed in.
    """

    __slots__ = ("verified", "mfa_enabled")

    #: Whether the account is verified or not.
    #:
    #: :type: :class:`bool`
    verified: bool

    #: Whether MFA is enabled or not.
    #:
    #: :type: :class:`bool`
    mfa_enabled: bool

    def __init__(self, global_state: model_cache.AbstractModelCache, payload):
        super().__init__(global_state, payload)
        self.verified = payload.get("verified", False)
        self.mfa_enabled = payload.get("mfa_enabled", False)


__all__ = ["User", "Member", "BotUser"]