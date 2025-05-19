from fastapi import FastAPI, WebSocket
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

import largeModel
import json
from schemas import chatRequest
from openai import AsyncOpenAI

import route_user
import route_file
import route_project
import route_settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Fname, Content-Disposition"]
)

app.include_router(route_user.router)
app.include_router(route_file.router)
app.include_router(route_project.router)
app.include_router(route_settings.router)


@app.get("/")
def read_root():
    raise HTTPException(
        status_code=403, detail="Accessing the root is not allowed")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        message_dict = json.loads(message)
        if message_dict["type"] == "test":
            if message_dict["message"] == "":
                continue
            if message_dict["endpoint"] == "":
                continue
            if message_dict["model"] == "":
                continue
            client = AsyncOpenAI(base_url=message_dict["endpoint"],
                                 api_key=message_dict["key"])

            async for text in largeModel.get_ai_response(message_dict["message"], client, message_dict["model"]):
                await websocket.send_text(text)
        elif message_dict["type"] == "project":
            req = chatRequest(
                project_name=message_dict["project_name"],
                paragraph_title=message_dict["paragraph_title"],
                paragraph_current_content=message_dict["paragraph_current_content"],
                user_prompt=message_dict["user_prompt"],
                refs=message_dict["refs"]
            )
            async for text in largeModel.chat_project(req, message_dict["token"]):
                await websocket.send_text(text)
