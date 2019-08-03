# FastAPI-compatible API Client Generator

Generate a sync+async IDE-friendly API client from an OpenAPI spec. Designed primarily to work with FastAPI.

Look inside `example/fastapi_client` to see what the generated output looks like. 

The generated client has the following dependencies:
* `fastapi`, `pydantic`, `starlette`
* `httpx` for networking
* `typing_extensions` for Enums (I hope to remove this eventually)

The generated client also has built-in support for the OAuth2.0 password flow; see `example/usage_example.py`. 

**Warning: This is still in the proof-of-concept phase.** It has some known bugs, and even more unknown.

If you try this out, please help me by reporting any issues you notice! 

## Client library usage

```python
from fastapi_client.api_client import ApiClient, Apis
from fastapi_client.models import Pet

client = ApiClient(host="http://localhost")
apis = Apis(client)

# Async API
async def get_pet_1() -> Pet:
    return await apis.pet_api.get_pet_by_id(pet_id=1)

# Sync API 
pet_2 = apis.pet_api.get_pet_by_id_sync(pet_id=2)
```

See `example/fastapi_client` for an example generated client library,
and `example/usage_example.py` for some more complex usage. 

## Generating the client library

Using the generator looks like
```bash
./scripts/generate.sh <client_library_name> -i <path_to_openapi_spec>
```
and will produce a client library at `generated/<client_library_name>`

For example, running
```bash
./scripts/generate.sh fastapi_client -i https://petstore.swagger.io/v2/swagger.json
```
produces the example client, and places it in `generated/fastapi_client`.


#### Generation details

* The only local dependencies for generation are `docker` and standard command line tools.
* `openapi-generator` is used to generate the code from the openapi spec
    * The custom templates are located in `openapi-python-templates`
* `autoflake`, `isort`, and `black` are used to format the code after generation
* To generate a client for a default FastAPI app running on localhost:

        ./scripts/generate.sh my_client -i http://localhost/openapi.json


## Contributing

Pull requests are welcome!
