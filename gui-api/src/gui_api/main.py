import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

logger = logging.getLogger()


async def healthcheck(request):
    return PlainTextResponse("", status_code=204)


async def search(request):
    logger.info("Search: %s", request)
    return JSONResponse({"res": "placeholder"})


app = Starlette(
    debug=True,
    routes=[
        Route("/", healthcheck),
        Route("/search", search, methods=["POST"]),
    ],
)
