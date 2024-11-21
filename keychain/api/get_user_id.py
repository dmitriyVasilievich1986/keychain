from __future__ import annotations

from flask import g


def get_user_id() -> int | None:
    """
    Retrieves the user ID from the current user object.

    Returns:
        int | None: The user ID if available, otherwise None.
    """

    return getattr(g.user, "id", None)
