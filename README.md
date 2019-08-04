# FastAPI-compatible API Client Generator

Generate a sync+async IDE-friendly API client from an OpenAPI spec. (Designed primarily to work with FastAPI.)

Look inside `example/fastapi_client` to see what the generated output looks like. 

The generated client has the following dependencies:
* `fastapi`, `pydantic`, `starlette`
* `httpx` for networking
* `typing_extensions` for Enums (I hope to remove this eventually)

The generated client also has built-in support for the OAuth2.0 password flow;
see `example/usage_example.py` (or `tests/auth_app.py` and `tests/test_auth.py`). 

**Warning: This is still in the proof-of-concept phase.**

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

If you want to replace `<client_library_name>` with a relative package name, I currently recommend using `sed`
(this may improve eventually). For example, to place the client in `package.my_client`: 

        ./scripts/generate.sh my_client -i http://localhost/openapi.json
        
        find generated/my_client -type f -name "*.py" -exec \
            sed -i'' -e 's/from my_client/from package.my_client/g' {} +

### With FastAPI

* To generate a client for a default FastAPI app running on localhost (NOT inside a docker container):

        ./scripts/generate.sh my_client -i http://localhost/openapi.json

* Since the generator runs inside docker, if your server is also running in a docker container,
[you may need to provide a special hostname](https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach).
On MacOS, this looks like:
 
        ./scripts/generate.sh my_client -i http://host.docker.internal/api/v1/openapi.json


### Generation details

* The only local dependencies for generation are `docker` and standard command line tools.
* `openapi-generator` is used to generate the code from the openapi spec
    * The custom templates are located in `openapi-python-templates`
* `autoflake`, `isort`, and `black` are used to format the code after generation


## Contributing

There are a variety of make rules for setup/testing; here are some highlights:
* `make develop`: Sets up the local development environment.
* `make regenerate`: Regenerates the example client from the example's openapi.json and the templates.
    * Note: *This will overwrite changes!* Make sure you commit (or edit the templates) before running this.
* `make`: Checks that isort, black, flake8, mypy, and pytest all pass
* `make testcov`: Generates a coverage report for the tests.
 
Pull requests are welcome and appreciated!
