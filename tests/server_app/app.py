"""
Test harness app implementing the server endpoints required for
fastapi_client testing.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from .routers import auth_router, client_router

app = FastAPI(debug=True)


@app.on_event("startup")
async def startup() -> None:
    """
    Use the operation names as operation_id. The generated names are not friendly.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


app.include_router(auth_router(), tags=["auth"])
app.include_router(client_router(), tags=["client"])


def main() -> None:
    """ Kick off uvicorn on port 8000"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
