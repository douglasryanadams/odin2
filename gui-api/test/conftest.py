from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

import fakeredis
import httpx2
from httpx2 import AsyncClient, MockTransport
from pytest import fixture
from starlette.applications import Starlette
from starlette.testclient import TestClient

from gui_api.kv import KeyValConnection
from gui_api.main import GlobalResources, build_app


@fixture
def fake_redis() -> KeyValConnection:
    return fakeredis.FakeAsyncRedis(decode_responses=True)


def handler(request: httpx2.Request):
    if request.url.path.startswith("/api-search/brave"):
        return httpx2.Response(200, json={"result": "placeholder"})
    else:
        raise NotImplementedError("This api-search API is not Mocked")


@fixture
def fake_search_api_client() -> AsyncClient:
    mock_transport = MockTransport(handler=handler)
    return AsyncClient(base_url="/api-search", transport=mock_transport)


@fixture
def test_client(fake_redis: KeyValConnection, fake_search_api_client: AsyncClient) -> Iterator[TestClient]:
    @asynccontextmanager
    async def mock_lifespan(_: Starlette) -> AsyncIterator[GlobalResources]:
        async with fake_search_api_client:
            yield {"redis_connection": fake_redis, "search_api_client": fake_search_api_client, "base_path": ""}

    app = build_app(lifespan=mock_lifespan)
    with TestClient(app) as client:
        yield client
