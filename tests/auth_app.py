import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi_client.password_flow_client import TokenSuccessResponse

app = FastAPI(debug=True)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/token")


@app.get("/")
def access(token: str = Depends(reusable_oauth2)) -> JSONResponse:
    if token != "access_token":
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")

    return JSONResponse(content={"result": "success"})


@app.post("/token")
def get_tokens(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenSuccessResponse:
    if form_data.username == "username" and form_data.password == "password":
        return TokenSuccessResponse(access_token="access_token", token_type="bearer")
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")


uvicorn.run(app, host="0.0.0.0", port=8000)
