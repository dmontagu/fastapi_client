# -*- coding: utf-8 -*-
"""
Setup file for pytest.
Sets up paths, start and stops the test server & builds the client module
"""

import os
import shutil
import signal
import subprocess
import sys
import time
from multiprocessing import Process

import pytest
from fastapi import FastAPI

from .server_app import app

ROOT = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(ROOT)


LOG_DIR = os.path.join(ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

CLIENT_NAME = "generated_client"
CLIENT_DIR = os.path.join(ROOT, CLIENT_NAME)


def run_server(app: FastAPI, host: str, port: int, log_level: str, log_dir: str) -> None:
    import uvicorn

    with open(os.path.join(log_dir, "server.log"), "w") as stdout:
        sys.stdout = stdout
        sys.stderr = stdout
        uvicorn.run(app, host=host, port=port, log_level=log_level)


PROC = Process(
    target=run_server,  # run_server,
    args=(app,),
    kwargs={"host": "localhost", "port": 8000, "log_level": "info", "log_dir": LOG_DIR},
    daemon=True,
)


def create_generated_client() -> None:
    """
    Invoke scripts/generate.sh to rebuild the test client from the running server app
    """
    print("Generating client")

    delete_generated_client()
    args = [
        "{}/../scripts/generate.sh".format(ROOT),
        "-i",
        "http://localhost:8000/openapi.json",
        "-p",
        CLIENT_NAME,
        "--include-auth",
        "-o",
        ROOT,
        "-t",
        "/tmp",
        "-m",
    ]

    process_result = subprocess.run(args, capture_output=True)

    with open(os.path.join(LOG_DIR, "generation.log"), "wb") as file:
        file.write(process_result.stdout)

    with open(os.path.join(LOG_DIR, "generation.err"), "wb") as file:
        file.write(process_result.stderr)

    if process_result.returncode != 0:  # pragma: no cover
        if process_result.stderr:
            sys.stderr.write(process_result.stderr.decode("utf-8"))
        pytest.exit(
            "Failed to generate client api, code {}"
            "\nLogs are in logs/generation.log and logs/generation.err".format(process_result.returncode),
            returncode=process_result.returncode,
        )

    print("Client created in {}, logs in logs/generation.log\n".format(CLIENT_DIR))


def delete_generated_client() -> None:
    """
    Delete the generated client
    """
    shutil.rmtree(CLIENT_DIR, ignore_errors=True)


def pytest_configure() -> None:  # pragma: no cover
    """
    Called before the test run.
    Start the server process, generate the test client
    """
    print("Starting server app")
    PROC.start()
    time.sleep(1)
    if PROC.exitcode is not None:
        pytest.exit("Failed to start the server, exit code {}\nLogs are in logs/server.log".format(PROC.exitcode))
        return

    create_generated_client()


def pytest_unconfigure() -> None:  # pragma: no cover
    """
    Called after the test run
    Kill the server (forcibly if it doesn't stop with 5 seconds of being asked nicely)
    """
    if PROC.exitcode is None:
        assert PROC.pid is not None  # not sure if this can happen (mypy error); if it does, be explicit
        os.kill(PROC.pid, signal.SIGINT)
        PROC.join(5)
        if PROC.exitcode is None:
            PROC.kill()
            PROC.join()
        print("\nServer app terminated, logs in logs/server.log")
