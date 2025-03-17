import mysql.connector.connection as mysql_connection


def getProjects(mysql_connection: mysql_connection.MySQLConnection, unique_id: str):
    '''
    @param unique_id: The unique identifier of the user
    @return: The projects of the user
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT `project_id`, `project_name` FROM `user_projects` WHERE `UNIQUE_ID` = %s AND `deleted`=0;", (unique_id,))
    projects = mysql_cursor.fetchall()
    projects = [{"project_id": project[0], "project_name": project[1]}
                for project in projects]
    mysql_cursor.close()
    return projects


def createProject(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, project_name: str):
    '''
    @param unique_id: The unique identifier of the user
    @param project_name: The name of the project
    @return: The success of the operation
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "INSERT INTO `user_projects` (`UNIQUE_ID`, `project_name`, `paragraphs`) VALUES (%s, %s, '[]');", (unique_id, project_name))
    mysql_connection.commit()
    id = mysql_cursor.lastrowid
    mysql_cursor.close()

    return id


def renameProject(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, project_id: int, new_name: str):
    '''
    @param unique_id: The unique identifier of the user
    @param project_id: The id of the project
    @param new_name: The new name of the project
    @return: The success of the operation
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "UPDATE `user_projects` SET `project_name`=%s WHERE `UNIQUE_ID`=%s AND `project_id`=%s AND `deleted`=0;", (new_name, unique_id, project_id))
    mysql_connection.commit()
    mysql_cursor.close()
    return True


def getProjectName(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, project_id: int):
    '''
    @param unique_id: The unique identifier of the user
    @param project_id: The id of the project
    @return: The name of the project
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT `project_name` FROM `user_projects` WHERE `UNIQUE_ID`=%s AND `project_id`=%s AND `deleted`=0;", (unique_id, project_id))
    project_name = mysql_cursor.fetchone()[0]
    mysql_cursor.close()
    return project_name


def deleteProject(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, project_id: int):
    '''
    @param unique_id: The unique identifier of the user
    @param project_id: The id of the project
    @return: The success of the operation
    '''
    mysql_cursor = mysql_connection.cursor()
    # mysql_cursor.execute(
    #    "DELETE FROM `user_projects` WHERE `UNIQUE_ID`=%s AND `project_id`=%s;", (unique_id, project_id))
    mysql_cursor.execute(
        "UPDATE `user_projects` SET `deleted`=1 WHERE `UNIQUE_ID`=%s AND `project_id`=%s;", (unique_id, project_id))
    mysql_connection.commit()
    mysql_cursor.close()
    return True


def getParagraphs(mysql_connection: mysql_connection.MySQLConnection,  unique_id: str, project_id: int):
    '''
    @param project_id: The id of the project
    @return: The paragraphs of the project
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT `paragraphs` FROM `user_projects` WHERE `project_id` = %s AND `UNIQUE_ID` = %s AND `deleted`=0;", (project_id, unique_id))
    paragraphs = mysql_cursor.fetchone()[0]
    mysql_cursor.close()
    return paragraphs


def saveProject(mysql_connection: mysql_connection.MySQLConnection, unique_id: str, project_id: int, paragraphs: str):
    '''
    @param unique_id: The unique identifier of the user
    @param project_id: The id of the project
    @param paragraphs: The paragraphs of the project
    @return: The success of the operation
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "UPDATE `user_projects` SET `paragraphs`=%s WHERE `project_id`=%s AND `UNIQUE_ID`=%s AND `deleted`=0;", (paragraphs, project_id, unique_id))
    mysql_connection.commit()
    mysql_cursor.close()
    return True
