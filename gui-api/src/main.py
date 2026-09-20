import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

logger = logging.getLogger()


async def homepage(request):
    return JSONResponse({"hello": "world"})


async def search(request):
    logger.info("Search: %s", request)
    return JSONResponse({"res": "placeholder"})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/search", search, methods=["POST"]),
    ],
)
