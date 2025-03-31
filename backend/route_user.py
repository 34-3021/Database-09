from schemas import NativeAccount, Token
import authenticate
import mysql.connector
from dbpassword import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
from fastapi import APIRouter

router = APIRouter()


@router.post("/login/verifyToken")
def verify_token(t: Token):
    token = t.token
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, token)
    mysql_connection.close()
    return {"success": success}


@router.post("/login/tauth")
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


@router.post("/register/native")
def register(account: NativeAccount):
    username = account.username
    password = account.password
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success, token, error_message = authenticate.registerWithPassword(
        mysql_connection, username, password)
    mysql_connection.close()
    return {"success": success, "token": token, "error_message": error_message}


@router.post("/login/native")
def login(account: NativeAccount):
    username = account.username
    password = account.password
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success, token, error_message = authenticate.loginWithPassword(
        mysql_connection, username, password)
    mysql_connection.close()
    return {"success": success, "token": token, "error_message": error_message}
