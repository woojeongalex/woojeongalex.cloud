from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


_ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.GUEST: {"read:public"},
    Role.USER: {"read:public", "read:private", "write:own"},
    Role.ADMIN: {"read:public", "read:private", "write:own", "write:all", "admin:all"},
}


def has_permission(role: str, permission: str) -> bool:
    try:
        r = Role(role)
    except ValueError:
        return False
    return permission in _ROLE_PERMISSIONS.get(r, set())
