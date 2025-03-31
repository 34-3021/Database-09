from fastapi import APIRouter
from fastapi import Header
from typing import Annotated
import mysql.connector
from dbpassword import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
import authenticate
import largeModel
from schemas import Settings, getModelsRequest, Token

router = APIRouter()


@router.post("/settings/getUniqueID")
def get_unique_id(t: Token):
    token = t.token
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    mysql_connection.close()
    return {"unique_id": unique_id}


@router.get("/user/settings")
def get_user_settings(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    settings = authenticate.getSettings(mysql_connection, unique_id)
    mysql_connection.close()
    return {"success": True, "settings": settings}


@router.post("/user/settings/set")
def set_user_settings(payload: Settings, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = authenticate.setSettings(
        mysql_connection, unique_id, payload.data)
    mysql_connection.close()
    return {"success": success}


@router.post("/llm/getModels")
def get_models(request: getModelsRequest):
    models = largeModel.get_models(request.endpoint, request.api_key)
    return models
