from fastapi import File, UploadFile, Header
import mysql.connector.connection as mysql_connection
import authenticate
import hashlib
import os


async def processUpload(mysql_connection: mysql_connection.MySQLConnection, token: str, upload: UploadFile):
    '''
    @param token: The token to be verified
    @param upload: The file to be processed
    @return: success
    '''
    # get unique id
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    if unique_id == None:
        return False

    # calc hash
    h = hashlib.sha256()

    for chunk in upload.file:
        h.update(chunk)

    hash = h.hexdigest()
    filesize = upload.size

    await upload.seek(0)

    # check if exists in db table `files`:`id`,`size`,`sha256`
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT * FROM `files` WHERE `sha256` = %s;", (hash,))
    file = mysql_cursor.fetchone()
    if file is None:
        # store to ./userdata/files/`hash`[0:2]/hash.dat
        directory = f"./userdata/files/{hash[0:2]}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"./userdata/files/{hash[0:2]}/{hash}.dat", "wb") as f:
            for chunk in upload.file:
                f.write(chunk)

        # insert into db table `files`:`id`,`size`,`sha256`
        mysql_cursor.execute(
            "INSERT INTO `files` (`size`, `sha256`) VALUES (%s, %s);", (filesize, hash))
        mysql_connection.commit()
        mysql_cursor.execute(
            "SELECT * FROM `files` WHERE `sha256` = %s;", (hash,))
        file = mysql_cursor.fetchone()
    fileid = file[0]

    # insert into `user_files` UNIQUE_ID fileid name(=filename)

    mysql_cursor.execute(
        "INSERT INTO `user_files` (`UNIQUE_ID`, `fileid`, `name`) VALUES (%s, %s, %s);", (unique_id, fileid, upload.filename))
    mysql_connection.commit()
    mysql_cursor.close()
    return True


def getUserFileList(mysql_connection: mysql_connection.MySQLConnection, token: str, batch_size: int, offset: int):
    '''
    @param token: The token to be verified
    @return: A list of files
    '''
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    if unique_id == None:
        return None

    mysql_cursor = mysql_connection.cursor()
    # SELECT name,(SELECT size from `files` where id=fileid) AS fsize FROM `user_files` WHERE `UNIQUE_ID`="" ORDER BY seq DESC LIMIT batch_size OFFSET offset
    mysql_cursor.execute(
        "SELECT `name`,(SELECT size from `files` where `id`=`fileid`),`seq` FROM `user_files` WHERE `UNIQUE_ID`=%s ORDER BY `seq` DESC LIMIT %s OFFSET %s;", (unique_id, batch_size, offset))
    files = mysql_cursor.fetchall()

    files = [{"name": file[0], "size": file[1], "seq": file[2]}
             for file in files]

    # totalfiles
    mysql_cursor.execute(
        "SELECT COUNT(*) FROM `user_files` WHERE `UNIQUE_ID`=%s;", (unique_id,))
    totalfiles = mysql_cursor.fetchone()[0]

    mysql_cursor.close()
    return files, totalfiles


def getFile(mysql_connection: mysql_connection.MySQLConnection, token: str, seq: int):
    '''
    @param token: The token to be verified
    @param file_id: The id of the file
    @return: The file,name
    '''
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    if unique_id == None:
        return None

    mysql_cursor = mysql_connection.cursor()

    mysql_cursor.execute(
        "SELECT `name`,`fileid` FROM `user_files` WHERE `UNIQUE_ID`=%s AND `seq`=%s;", (unique_id, seq))
    file = mysql_cursor.fetchone()
    if file == None:
        return None

    mysql_cursor.execute(
        "SELECT `sha256` FROM `files` WHERE `id`=%s;", (file[1],))
    filed = mysql_cursor.fetchone()
    if filed == None:
        return None

    with open(f"./userdata/files/{filed[0][0:2]}/{filed[0]}.dat", "rb") as f:
        content = f.read()

    mysql_cursor.close()
    return content, file[0]


def deleteFile(mysql_connection: mysql_connection.MySQLConnection, token: str, seq: int):
    '''
    @param token: The token to be verified
    @param seq: The id of the file
    @return: success
    '''
    unique_id = authenticate.getUniqueID(mysql_connection, token)
    if unique_id == None:
        return False

    mysql_cursor = mysql_connection.cursor()

    mysql_cursor.execute(
        "DELETE FROM `user_files` WHERE `UNIQUE_ID`=%s AND `seq`=%s;", (unique_id, seq))
    mysql_connection.commit()
    mysql_cursor.close()

    return True
