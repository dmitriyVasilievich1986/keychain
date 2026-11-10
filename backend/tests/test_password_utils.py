"""Tests for the API v1 password route helpers."""

from datetime import datetime, timezone

from keychain.modules.routers.api.v1.password.utils import build_fields
from keychain.modules.routers.models.request.password import PasswordFieldCreate


def test_build_fields_keeps_deleted_at() -> None:
    """A field sent with ``deletedAt`` stays soft-deleted; other fields stay active."""
    deleted_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    request_fields = [
        PasswordFieldCreate.model_validate({"name": "login", "values": [{"value": "me"}]}),
        PasswordFieldCreate.model_validate(
            {"name": "old", "values": [{"value": "x"}], "deletedAt": deleted_at.isoformat()}
        ),
    ]

    fields = build_fields(request_fields)

    assert [field.position for field in fields] == [0, 1]
    assert fields[0].deleted_at is None
    assert fields[1].deleted_at == deleted_at
