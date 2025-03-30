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
import requests
from openai import AsyncOpenAI, OpenAI

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


@app.get("/search")
def search_in_files(keyword: str, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)

    resp = requests.post("http://localhost:8005/query", json={
        "query_text": keyword, "unique_id": unique_id})
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code,
                            detail="Error in query")
    result: dict = resp.json()
    keys = result.keys()
    fname_sha256 = filel.getFileNames(
        mysql_connection, unique_id, keys)
    dic = {}
    for i in range(len(fname_sha256)):
        dic[fname_sha256[i][1]] = fname_sha256[i][0]
    res = {}
    for i in keys:
        res[dic[i]] = result[i]
    mysql_connection.close()
    return {"result": res}


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


async def chat_project(req: chatRequest,  infiniDocToken: str):
    mysql_connection = gen_mysql_connection_and_validate_token(infiniDocToken)
    # todo implement chat
    # response = req.user_prompt+" received"
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    settings = authenticate.getSettings(mysql_connection, unique_id)
    if settings["endpoint"] == "":
        raise HTTPException(status_code=400, detail="Endpoint not set")
    if settings["model"] == "":
        raise HTTPException(status_code=400, detail="Model not set")
    client = OpenAI(
        api_key=settings["key"],
        base_url=settings["endpoint"]
    ) if settings["key"] != "" else OpenAI(
        base_url=settings["endpoint"]
    )
    msg, response = largeModel.get_ai_response_primary(
        req.project_name, req.paragraph_title, req.paragraph_current_content, req.user_prompt, client, settings[
            "model"]
    )
    yield "--SYSTEM--"
    yield msg[0]["content"]
    yield "--DONE--"
    yield "--AI PROG--"
    yield response
    yield "--DONE--"
    yield "--SYSTEM--"
    kwds = [s.strip() for s in response]
    additional_info_s = ""
    if kwds[0] != "No":
        resp = requests.post("http://localhost:8005/querymultiple", json={
            "query_texts": kwds, "unique_id": unique_id})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code,
                                detail="Error in query")
        result: dict = resp.json()
        keys = result.keys()
        fname_sha256 = filel.getFileNames(
            mysql_connection, unique_id, keys)
        dic = {}
        for i in range(len(fname_sha256)):
            dic[fname_sha256[i][1]] = fname_sha256[i][0]
        res = {}
        for i in keys:
            res[dic[i]] = result[i]
        for i in res.keys():
            additional_info_s += "In document " + i + ":\n"
            for j in res[i].keys():
                additional_info_s += "In " + j + ":\n" + res[i][j] + "\n"
        additional_info_s += "\n"
    client2 = AsyncOpenAI(
        api_key=settings["key"],
        base_url=settings["endpoint"]
    ) if settings["key"] != "" else AsyncOpenAI(
        base_url=settings["endpoint"]
    )
    yield additional_info_s
    yield "--DONE--"
    yield "--AI--"
    # get_ai_response_secondary is async function
    async for text in largeModel.get_ai_response_secondary(
            additional_info_s, msg, client2, settings["model"]):
        yield text
    yield "--DONE--"
    yield "--DDONE--"

    # return {"success": True, "response": response, "msg_history": msg}


async def get_ai_response(message: str, client: AsyncOpenAI, model: str) -> AsyncGenerator[str, None]:
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
        # key is optional
        if message_dict["type"] == "test":
            if message_dict["message"] == "":
                continue
            if message_dict["endpoint"] == "":
                continue
            if message_dict["model"] == "":
                continue
            client = AsyncOpenAI(base_url=message_dict["endpoint"],
                                 api_key=message_dict["key"])

            async for text in get_ai_response(message_dict["message"], client, message_dict["model"]):
                await websocket.send_text(text)
        elif message_dict["type"] == "project":
            req = chatRequest(
                project_name=message_dict["project_name"],
                paragraph_title=message_dict["paragraph_title"],
                paragraph_current_content=message_dict["paragraph_current_content"],
                user_prompt=message_dict["user_prompt"]
            )
            async for text in chat_project(req, message_dict["token"]):
                await websocket.send_text(text)
