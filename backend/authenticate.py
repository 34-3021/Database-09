from tauthAuthenticator import tauthAuthenticator
import random
import string
import mysql.connector.connection as mysql_connection
import mysql.connector
import authenticate
import time
import regex
import hashlib
from fastapi import HTTPException
from dbpassword import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE


def gen_mysql_connection_and_validate_token(token: str) -> mysql_connection.MySQLConnection:
    mysql_connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    success = authenticate.verifyLoginStatus(mysql_connection, token)
    if not success:
        mysql_connection.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    return mysql_connection


def validateUserName(username: str):
    '''
    @param username: The username to be validated
    @return: success
    '''
    # >=4 <= 32
    # a-zA-Z_-0-9
    if len(username) < 4 or len(username) > 32:
        return False
    if not regex.match("^[a-zA-Z0-9_-]*$", username):
        return False
    return True


def validatePassword(password: str):
    '''
    @param password: The password to be validated
    @return: success
    '''
    # must be a valid sha256 hexstring
    password = password.lower()
    if len(password) != 64:
        return False
    if not regex.match("^[a-f0-9]*$", password):
        return False
    return True


def verifyLoginStatus(mysql_connection: mysql_connection.MySQLConnection, infinidoc_token: str):
    '''
    @param infinidoc_token: The token to be verified
    @return: success
    '''
    mysql_cursor = mysql_connection.cursor()

    # get token from db
    mysql_cursor.execute(
        "SELECT * FROM `tokens` WHERE `TOKEN` = %s;", (infinidoc_token,))
    token = mysql_cursor.fetchone()
    mysql_cursor.close()

    if token is None:
        return False

    return True


def getUniqueID(mysql_connection: mysql_connection.MySQLConnection, infinidoc_token: str):
    '''
    @param infinidoc_token: The token to be verified
    @return: The unique identifier of the user
    '''
    mysql_cursor = mysql_connection.cursor()

    # get token from db
    mysql_cursor.execute(
        "SELECT UNIQUE_ID FROM `tokens` WHERE `TOKEN` = %s;", (infinidoc_token,))
    token = mysql_cursor.fetchone()
    mysql_cursor.close()

    if token is None:
        return None

    return token[0]


def generateToken(mysql_connection: mysql_connection.MySQLConnection, UNIQUE_ID: str):
    '''
    @param UNIQUE_ID: The unique identifier of the user
    @return: A token that can be used to verify the user's identity
    '''
    # gen token of a length of 64
    infinidoc_token = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=64))

    mysql_cursor = mysql_connection.cursor()

    # insert token into db
    mysql_cursor.execute(
        "INSERT INTO `tokens` (`UNIQUE_ID`, `time_accessed`,`TOKEN`) VALUES (%s, %s, %s);", (UNIQUE_ID, str(int(time.time())), infinidoc_token))
    mysql_connection.commit()
    mysql_cursor.close()
    return infinidoc_token


def loginWithPassword(mysql_connection: mysql_connection.MySQLConnection, username: str, password: str):
    '''
    @param username: The username of the user
    @param password: The password of the user
    @return: A tuple of (success, token, error_message)
    '''
    password = password.lower()
    if not validateUserName(username):
        return False, "", "Invalid username scheme"
    if not validatePassword(password):
        return False, "", "Invalid password scheme"

    mysql_cursor = mysql_connection.cursor()

    # get user from db
    mysql_cursor.execute(
        "SELECT `username`,`password`,`salt`,`id` FROM `users` WHERE `USERNAME` = %s;", (username,))
    user = mysql_cursor.fetchone()
    if user is None:
        return False, "", "Invalid username or password"

    salt = user[2]
    password = password + salt
    password = hashlib.sha256(password
                              .encode()).hexdigest()
    if password != user[1]:
        return False, "", "Invalid username or password"

    unique_id = "INFINIDOC_" + str(user[3]) + "_V1"
    infinidoc_token = generateToken(mysql_connection, unique_id)
    return True, infinidoc_token, ""


def registerWithPassword(mysql_connection: mysql_connection.MySQLConnection, username: str, password: str):
    '''
    @param username: The username of the user
    @param password: The password of the user
    @return: A tuple of (success, token, error_message)
    '''
    password = password.lower()
    if not validateUserName(username):
        return False, "", "Invalid username scheme"
    if not validatePassword(password):
        return False, "", "Invalid password scheme"

    mysql_cursor = mysql_connection.cursor()

    # check if username exists

    mysql_cursor.execute(
        "SELECT * FROM `users` WHERE `USERNAME` = %s;", (username,))
    user = mysql_cursor.fetchone()
    if user is not None:
        return False, "", "Username already exists"

    salt = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=32))
    password = password + salt
    password = hashlib.sha256(password
                              .encode()).hexdigest()

    mysql_cursor.execute(
        "INSERT INTO `users` (`username`, `password`, `salt`) VALUES (%s, %s, %s);", (username, password, salt))

    mysql_connection.commit()
    # get autoincremented id
    mysql_cursor.execute(
        "SELECT id FROM `users` WHERE `USERNAME` = %s;", (username,))
    user = mysql_cursor.fetchone()
    mysql_cursor.close()
    unique_id = "INFINIDOC_" + str(user[0]) + "_V1"
    infinidoc_token = generateToken(mysql_connection, unique_id)
    return True, infinidoc_token, ""


def loginWithTAuthToken(mysql_connection: mysql_connection.MySQLConnection, token: str):
    '''
    @param token: The token to be verified
    @return: A tuple of (success, token)
    '''
    success, uid = tauthAuthenticator(token)

    if success:
        unique_id = "THIRD_PARTY_TAUTH_" + str(uid) + "_V1"
        infinidoc_token = generateToken(mysql_connection, unique_id)
        return True, infinidoc_token
    else:
        return False, ""


def getSettings(mysql_connection: mysql_connection.MySQLConnection, unique_id: str):
    '''
    @param unique_id: The unique identifier of the user
    @return: The settings of the user
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT `setting`,`value` FROM `user_settings` WHERE `UNIQUE_ID` = %s;", (unique_id,))
    settings = mysql_cursor.fetchall()
    # convert to dict
    settings = {setting: value for setting, value in settings}
    mysql_cursor.close()
    return settings


def setSettings(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, settings: dict):
    '''
    @param unique_id: The unique identifier of the user
    @param settings: The settings to be set
    @return: success
    '''
    mysql_cursor = mysql_connection.cursor()
    for setting, value in settings.items():
        mysql_cursor.execute(
            "INSERT INTO `user_settings` (`UNIQUE_ID`, `setting`, `value`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `value` = %s;", (unique_id, setting, value, value))
    mysql_connection.commit()
    mysql_cursor.close()
    return True
