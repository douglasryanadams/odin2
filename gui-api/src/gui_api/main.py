import hashlib
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict

import redis.asyncio as redis
from httpx2 import AsyncClient, HTTPStatusError
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.routing import Route
from starlette.types import Lifespan

from gui_api.kv import KeyValConnection

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()


class GlobalResources(TypedDict):
    redis_connection: KeyValConnection
    search_api_client: AsyncClient
    base_path: str


@dataclass(frozen=True)
class SearchRequest:
    query: str


class AsyncStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[GlobalResources]:
    redis_host = os.environ.get("REDIS_HOST", "gui-kv")
    redis_port = int(os.environ.get("REDIS_PORT", "6379"))
    logger.debug("Redis: %s:%s", redis_host, redis_port)

    search_api_url = os.environ.get("SEARCH_API_URL", "http://gui-client:8080/api-search")
    logger.debug("SEARCH_API_URL: %s", search_api_url)
    base_path = os.environ.get("BASE_PATH", "/api")
    logger.debug("Base Path: %s", base_path)

    redis_connection = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    async with AsyncClient(base_url=search_api_url) as search_api_client:
        yield {
            "redis_connection": redis_connection,
            "search_api_client": search_api_client,
            "base_path": base_path,
        }
    await redis_connection.aclose()


async def healthcheck(request: Request[GlobalResources]):
    return PlainTextResponse("", status_code=204)


async def _do_search(query_hash: str, query: str, redis_connection: KeyValConnection, search_client: AsyncClient) -> None:
    logger.info("Running search ...")
    await redis_connection.hset(query_hash, "status", AsyncStatus.STARTED)
    logger.info("POST /brave | query = %s", query)
    response = await search_client.post("/brave", json={"query": query}, follow_redirects=True)
    try:
        response.raise_for_status()
    except HTTPStatusError:
        await redis_connection.hset(query_hash, "status", AsyncStatus.FAILED)
    brave_result = response.json()
    logger.info("... search complete")
    await redis_connection.hset(query_hash, "results", brave_result["result"])
    await redis_connection.hset(query_hash, "status", AsyncStatus.SUCCEEDED)


async def search(request: Request[GlobalResources]):
    logger.info("Search: %s", request)
    redis_connection = request.state["redis_connection"]
    search_api_client = request.state["search_api_client"]
    base_path = request.state["base_path"]

    request_body = await request.json()
    logger.info("Search: %s", request_body)
    search_request = SearchRequest(**request_body)

    query_hash = hashlib.sha256(search_request.query.encode("utf-8")).hexdigest()
    logger.debug("Query Hash: %s", query_hash)

    await redis_connection.hset(query_hash, mapping={"query": search_request.query, "status": AsyncStatus.ACCEPTED, "results": "placeholder"})
    do_brave_search = BackgroundTask(_do_search, query_hash=query_hash, query=search_request.query, redis_connection=redis_connection, search_client=search_api_client)
    return RedirectResponse(url=f"{base_path}/async-result/{query_hash}", status_code=302, background=do_brave_search)


async def async_result(request: Request[GlobalResources]):
    redis_connection = request.state["redis_connection"]
    base_path = request.state["base_path"]

    query_hash = request.path_params["query_hash"]
    query_status = await redis_connection.hget(query_hash, "status")
    if not query_status:
        raise HTTPException(status_code=404, detail="Query not found.")
    if query_status == AsyncStatus.SUCCEEDED:
        query_result = await redis_connection.hget(query_hash, "results")
        return JSONResponse(query_result)
    if query_status == AsyncStatus.FAILED:
        raise HTTPException(status_code=500, detail="Search failed.")
    return RedirectResponse(url=f"{base_path}/async-result/{query_hash}", status_code=302)


def build_app(lifespan: Lifespan[Starlette] = lifespan) -> Starlette:
    return Starlette(
        debug=True,
        lifespan=lifespan,
        routes=[
            Route("/", healthcheck),
            Route("/search", search, methods=["POST"]),
            Route("/async-result/{query_hash}", async_result, methods=["GET"]),
        ],
    )
