# -*- coding: utf-8 -*-
"""
Allows the module to be run with python -m server_app
"""
if __name__ == "__main__":
    import uvicorn

    from .app import app

    uvicorn.run(app=app, host="localhost", port=8000, log_level="info")
