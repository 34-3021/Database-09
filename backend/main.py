from typing import Annotated, Union, AsyncGenerator

from fastapi import FastAPI, WebSocket
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
import websockets
import json
from openai import AsyncOpenAI

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


class deleteProjectRequest(BaseModel):
    project_id: int


class renameProjectRequest(BaseModel):
    new_name: str


class saveProjectRequest(BaseModel):
    paragraphs: str


class chatRequest(BaseModel):
    project_name: str
    paragraph_title: str
    paragraph_current_content: str
    user_prompt: str


def gen_mysql_connection_and_validate_token(token: str) -> mysql.connector.MySQLConnection:
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, token)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    return mysql_connection


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
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)

    result = await filel.processUpload(mysql_connection, infiniDocToken, file)
    mysql_connection.close()

    # Process the uploaded file here
    return result


@app.get("/fileList")
def file_list(infiniDocToken: Annotated[str | None, Header()] = None, limit: int = 10, offset: int = 0):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)

    files, totalfiles = filel.getUserFileList(
        mysql_connection, infiniDocToken, limit, offset)

    mysql_connection.close()
    return {"files": files, "totalfiles": totalfiles}


@app.get("/download")
def download_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)

    file, filename = filel.getFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return Response(content=file, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}", "Fname": filename})


@app.get("/delete")
def delete_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)

    success = filel.deleteFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return {"success": success}


@app.get("/user/settings")
def get_user_settings(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    settings = authenticate.getSettings(mysql_connection, unique_id)
    mysql_connection.close()
    return {"success": True, "settings": settings}


@app.post("/user/settings/set")
def set_user_settings(payload: Settings, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = authenticate.setSettings(
        mysql_connection, unique_id, payload.data)
    mysql_connection.close()
    return {"success": success}


@app.get("/project/get")
def get_projects(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    projects = projectManager.getProjects(mysql_connection, unique_id)
    mysql_connection.close()
    return {"projects": projects}


@app.post("/project/create")
def create_project(req: createProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    id = projectManager.createProject(
        mysql_connection, unique_id, req.project_name)
    mysql_connection.close()
    return {"success": True, "id": id}


@app.post("/project/delete")
def delete_project(req: deleteProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.deleteProject(
        mysql_connection, unique_id, req.project_id)
    mysql_connection.close()
    return {"success": success}


@app.post("/project/rename/{project_id}")
def rename_project(project_id: int, req: renameProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.renameProject(
        mysql_connection, unique_id, project_id, req.new_name)
    mysql_connection.close()
    return {"success": success}


@app.get("/project/getparagraphs/{project_id}")
def get_paragraphs(project_id: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    paragraphs = projectManager.getParagraphs(
        mysql_connection, unique_id, project_id)
    mysql_connection.close()
    return {"paragraphs": paragraphs}


@app.get("/project/name/{project_id}")
def get_project_name(project_id: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    project_name = projectManager.getProjectName(
        mysql_connection, unique_id, project_id)
    mysql_connection.close()
    return {"project_name": project_name}


@app.post("/project/save/{project_id}")
def save_project(project_id: int, req: saveProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.saveProject(
        mysql_connection, unique_id, project_id, req.paragraphs)
    mysql_connection.close()
    return {"success": success}


@app.post("/llm/getModels")
def get_models(request: getModelsRequest):
    models = largeModel.get_models(request.endpoint, request.api_key)
    return models


@app.post("/project/chat")
def chat_project(req: chatRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    # todo implement chat
    response = req.user_prompt+" received"
    mysql_connection.close()
    return {"success": True, "response": response}


async def get_ai_response(message: str, client: AsyncOpenAI, model: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant, skilled in explaining "
                    "complex concepts in simple terms."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield content


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Websocket for AI responses
    """
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        # input format
        # {"message":,"endpoint":,"key":,"model":}
        message_dict = json.loads(message)
        if message_dict["message"] == "":
            continue
        if message_dict["endpoint"] == "":
            continue
        if message_dict["model"] == "":
            continue
        # key is optional
        client = AsyncOpenAI(base_url=message_dict["endpoint"],
                             api_key=message_dict["key"])

        async for text in get_ai_response(message_dict["message"], client, message_dict["model"]):
            await websocket.send_text(text)
