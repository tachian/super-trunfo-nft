import inspect

from fastapi import FastAPI


async def call_registered_route(app: FastAPI, path: str) -> object:
    for route in app.routes:
        if getattr(route, "path", None) == path:
            result = route.endpoint()

            if inspect.isawaitable(result):
                return await result

            return result

    raise AssertionError(f"Route not registered: {path}")

