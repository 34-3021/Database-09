from typing import Union

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import mysql.connector
from dbpassword import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

import authenticate
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    # Adjust this to the specific origins you want to allow
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Token(BaseModel):
    token: str


class NativeAccount(BaseModel):
    username: str
    password: str


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
