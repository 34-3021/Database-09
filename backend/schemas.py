from pydantic import BaseModel


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
    refs: list[str]


class convertRequest(BaseModel):
    markdown: str
    target: str
