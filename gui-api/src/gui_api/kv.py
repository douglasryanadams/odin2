from collections.abc import Awaitable, Mapping
from typing import Protocol

from redis.typing import EncodableT, FieldT


class KeyValConnection(Protocol):
    def get(self, key: str, /) -> Awaitable[str | bytes | None]: ...
    def set(self, key: str, val: str, /) -> Awaitable[object]: ...

    def hget(self, name: str, key: str, /) -> Awaitable[str | bytes | None]: ...
    def hset(
        self,
        name: str,
        key: FieldT | None = None,
        value: EncodableT | None = None,
        mapping: Mapping[FieldT, EncodableT] | None = None,
        items: list[EncodableT] | None = None,
    ) -> Awaitable[int]: ...
