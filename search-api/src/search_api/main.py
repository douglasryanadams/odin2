import hashlib
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict

import redis.asyncio as redis
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.routing import Route
from starlette.types import Lifespan

from search_api.kv import KeyValConnection

logger = logging.getLogger()


class GlobalResources(TypedDict):
    redis_connection: KeyValConnection
    base_path: str


@dataclass(frozen=True)
class SearchRequest:
    query: str


class SearchStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[GlobalResources]:
    redis_host = os.environ.get("REDIS_HOST", "search-kv")
    redis_port = int(os.environ.get("REDIS_PORT", "6379"))
    base_path = os.environ.get("BASE_PATH", "/api-search")
    logger.debug("Redis: %s:%s", redis_host, redis_port)
    redis_connection = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    yield {
        "redis_connection": redis_connection,
        "base_path": base_path,
    }
    await redis_connection.aclose()


async def healthcheck(request: Request):
    return PlainTextResponse("", status_code=204)


async def _do_brave_search(query_hash: str, query: str, redis_connection: KeyValConnection) -> None:
    logger.info("Searching Brave ...")
    await redis_connection.hset(query_hash, "status", SearchStatus.STARTED)
    # TODO: Execute Search
    logger.info("... search complete")
    await redis_connection.hset(query_hash, "results", "placeholder")
    await redis_connection.hset(query_hash, "status", SearchStatus.SUCCEEDED)


async def brave(request: Request[GlobalResources]):
    redis_connection = request.state["redis_connection"]
    base_path = request.state["base_path"]

    request_body = await request.json()
    logger.info("Search: %s", request_body)
    search_request = SearchRequest(**request_body)

    query_hash = hashlib.sha256(search_request.query.encode("utf-8")).hexdigest()
    logger.debug("Query Hash: %s", query_hash)

    await redis_connection.hset(query_hash, mapping={"query": search_request.query, "status": SearchStatus.ACCEPTED, "results": "placeholder"})
    do_brave_search = BackgroundTask(_do_brave_search, query_hash=query_hash, query=search_request.query, redis_connection=redis_connection)
    # Guidance on reason for HTTP 303 here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/302
    return RedirectResponse(url=f"{base_path}/search-result/{query_hash}", status_code=302, background=do_brave_search)


async def search_result(request: Request[GlobalResources]):
    redis_connection = request.state["redis_connection"]
    base_path = request.state["base_path"]

    query_hash = request.path_params["query_hash"]
    query_status = await redis_connection.hget(query_hash, "status")
    if not query_status:
        raise HTTPException(status_code=404, detail="Query not found.")
    if query_status == "SUCCEEDED" or query_status == "FAILED":
        query_result = await redis_connection.hget(query_hash, "results")
        return JSONResponse(query_result)
    else:
        return RedirectResponse(url=f"{base_path}/search-result/{query_hash}", status_code=302)


def build_app(lifespan: Lifespan[Starlette] = lifespan) -> Starlette:
    return Starlette(
        debug=True,
        lifespan=lifespan,
        routes=[
            Route("/", healthcheck),
            Route("/brave", brave, methods=["POST"]),
            Route("/search-result/{query_hash}", search_result, methods=["GET"]),
        ],
    )
