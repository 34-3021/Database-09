import mysql.connector.connection as mysql_connection


def getProjects(mysql_connection: mysql_connection.MySQLConnection, unique_id: str):
    '''
    @param unique_id: The unique identifier of the user
    @return: The projects of the user
    '''
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute(
        "SELECT `project_id`, `project_name` FROM `user_projects` WHERE `UNIQUE_ID` = %s;", (unique_id,))
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
        "INSERT INTO `user_projects` (`UNIQUE_ID`, `project_name`) VALUES (%s, %s);", (unique_id, project_name))
    mysql_connection.commit()
    id = mysql_cursor.lastrowid
    mysql_cursor.close()

    return id
