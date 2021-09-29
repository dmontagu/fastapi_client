import inspect

from pydantic import BaseModel

from example.client import models
from client.api_client import AsyncApiClient, AsyncApis, SyncApiClient, SyncApis # noqa F401

for model in inspect.getmembers(models, inspect.isclass):
    if model[1].__module__ == "example.client.models":
        model_class = model[1]
        if isinstance(model_class, BaseModel):
            model_class.update_forward_refs()
