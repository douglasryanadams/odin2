from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import fakeredis
from pytest import fixture
from starlette.applications import Starlette
from starlette.testclient import TestClient

from search_api.kv import KeyValConnection
from search_api.main import GlobalResources, build_app


@fixture
def fake_redis() -> KeyValConnection:
    return fakeredis.FakeAsyncRedis(decode_responses=True)


@fixture
def test_client(fake_redis: KeyValConnection):
    @asynccontextmanager
    async def mock_lifespan(_: Starlette) -> AsyncIterator[GlobalResources]:
        yield {"redis_connection": fake_redis, "base_path": ""}

    app = build_app(lifespan=mock_lifespan)
    with TestClient(app) as client:
        yield client
