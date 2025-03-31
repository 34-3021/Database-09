from schemas import createProjectRequest, deleteProjectRequest, renameProjectRequest, saveProjectRequest
from fastapi import Header
from typing import Annotated
import projectManager
import authenticate
from fastapi import APIRouter

router = APIRouter()


@router.get("/project/get")
def get_projects(infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    projects = projectManager.getProjects(mysql_connection, unique_id)
    mysql_connection.close()
    return {"projects": projects}


@router.post("/project/create")
def create_project(req: createProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    id = projectManager.createProject(
        mysql_connection, unique_id, req.project_name)
    mysql_connection.close()
    return {"success": True, "id": id}


@router.post("/project/delete")
def delete_project(req: deleteProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.deleteProject(
        mysql_connection, unique_id, req.project_id)
    mysql_connection.close()
    return {"success": success}


@router.post("/project/rename/{project_id}")
def rename_project(project_id: int, req: renameProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.renameProject(
        mysql_connection, unique_id, project_id, req.new_name)
    mysql_connection.close()
    return {"success": success}


@router.get("/project/getparagraphs/{project_id}")
def get_paragraphs(project_id: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    paragraphs = projectManager.getParagraphs(
        mysql_connection, unique_id, project_id)
    mysql_connection.close()
    return {"paragraphs": paragraphs}


@router.get("/project/name/{project_id}")
def get_project_name(project_id: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    project_name = projectManager.getProjectName(
        mysql_connection, unique_id, project_id)
    mysql_connection.close()
    return {"project_name": project_name}


@router.post("/project/save/{project_id}")
def save_project(project_id: int, req: saveProjectRequest, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    success = projectManager.saveProject(
        mysql_connection, unique_id, project_id, req.paragraphs)
    mysql_connection.close()
    return {"success": success}
