from typing import Annotated, Union

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import File, UploadFile, Header
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import mysql.connector
from dbpassword import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

import authenticate
import filel
import largeModel
import projectManager

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    # Adjust this to the specific origins you want to allow
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Fname, Content-Disposition"]
)


class Token(BaseModel):
    token: str


class NativeAccount(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    data: dict


class getModelsRequest(BaseModel):
    endpoint: str
    api_key: str


class createProjectRequest(BaseModel):
    project_name: str


@app.get("/")
def read_root():
    raise HTTPException(
        status_code=403, detail="Accessing the root is not allowed")


@app.post("/settings/getUniqueID")
def get_unique_id(t: Token):
    token = t.token
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    mysql_connection.close()
    return {"unique_id": unique_id}


@app.post("/login/verifyToken")
def verify_token(t: Token):
    token = t.token
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, token)
    mysql_connection.close()
    return {"success": success}


@app.post("/login/tauth")
def login_with_tauth(t: Token):
    token = t.token
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success, infinidoc_token = authenticate.loginWithTAuthToken(
        mysql_connection, token)
    mysql_connection.close()
    if success:
        return {"success": True, "token": infinidoc_token}
    else:
        return {"success": False, "token": ""}


@app.post("/register/native")
def register(account: NativeAccount):
    username = account.username
    password = account.password
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success, token, error_message = authenticate.registerWithPassword(
        mysql_connection, username, password)
    mysql_connection.close()
    return {"success": success, "token": token, "error_message": error_message}


@app.post("/login/native")
def login(account: NativeAccount):
    username = account.username
    password = account.password
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success, token, error_message = authenticate.loginWithPassword(
        mysql_connection, username, password)
    mysql_connection.close()
    return {"success": success, "token": token, "error_message": error_message}


@app.post("/upload")
async def upload_file(file: UploadFile, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await filel.processUpload(mysql_connection, infiniDocToken, file)
    mysql_connection.close()

    # Process the uploaded file here
    return result


@app.get("/fileList")
def file_list(infiniDocToken: Annotated[str | None, Header()] = None, limit: int = 10, offset: int = 0):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    files, totalfiles = filel.getUserFileList(
        mysql_connection, infiniDocToken, limit, offset)

    mysql_connection.close()
    return {"files": files, "totalfiles": totalfiles}


@app.get("/download")
def download_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    file, filename = filel.getFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return Response(content=file, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}", "Fname": filename})


@app.get("/delete")
def delete_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    success = filel.deleteFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return {"success": success}


@app.get("/user/settings")
def get_user_settings(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    settings = authenticate.getSettings(mysql_connection, unique_id)
    mysql_connection.close()
    return {"success": success, "settings": settings}


@app.post("/user/settings/set")
def set_user_settings(payload: Settings, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = authenticate.setSettings(
        mysql_connection, unique_id, payload.data)
    mysql_connection.close()
    return {"success": success}


@app.get("/project/get")
def get_projects(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    projects = projectManager.getProjects(mysql_connection, unique_id)
    mysql_connection.close()
    return {"projects": projects}


@app.post("/project/create")
def create_project(req: createProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, infiniDocToken)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    id = projectManager.createProject(
        mysql_connection, unique_id, req.project_name)
    mysql_connection.close()
    return {"success": success, "id": id}


@app.post("/llm/getModels")
def get_models(request: getModelsRequest):
    models = largeModel.get_models(request.endpoint, request.api_key)
    return models
