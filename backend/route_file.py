from fastapi import APIRouter
from fastapi import FastAPI, UploadFile, Response, HTTPException, Header
import filel
import authenticate
import requests
import os
import random
import pypandoc
from typing import Annotated
from schemas import convertRequest
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/convert")
def convert_file(req: convertRequest):
    valid_formats = ["pdf", "docx", "html", "tex", "odt"]
    if req.target not in valid_formats:
        raise HTTPException(status_code=400, detail="Invalid target format")
    # Convert the file here
    random_filename = f"converted_{random.randint(0, 100000)}.{req.target}"
    # pypandoc.convert_text(req.markdown, req.target, format="md", extra_args=["--standalone", "--pdf-engine=xelatex", "-M", "mainfont:微软雅黑", "-M", "sansfont:微软雅黑", "-M", "monofont:微软雅黑"],
    pypandoc.convert_text(req.markdown, req.target, format="md", extra_args=["--pdf-engine=xelatex", "-V", "CJKmainfont=\"SimSun\""],
                          outputfile=random_filename
                          )
    # Check if the conversion was successful
    if not os.path.exists(random_filename):
        raise HTTPException(status_code=500, detail="Conversion failed")
    with open(random_filename, "rb") as f:
        output = f.read()

    os.remove(random_filename)

    # return the converted file in binary format
    return Response(content=output, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename=converted.{req.target}", "Fname": f"converted.{req.target}"})


@router.post("/upload")
async def upload_file(file: UploadFile, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)

    result = await filel.processUpload(mysql_connection, infiniDocToken, file)
    mysql_connection.close()

    # Process the uploaded file here
    return result


@router.get("/fileList")
def file_list(infiniDocToken: Annotated[str | None, Header()] = None, limit: int = 10, offset: int = 0):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)

    files, totalfiles = filel.getUserFileList(
        mysql_connection, infiniDocToken, limit, offset)

    mysql_connection.close()
    return {"files": files, "totalfiles": totalfiles}


@router.get("/download")
def download_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)

    file, filename = filel.getFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return Response(content=file, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}", "Fname": filename})


@router.get("/delete")
def delete_file(seq: int, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)

    success = filel.deleteFile(mysql_connection, infiniDocToken, seq)
    mysql_connection.close()

    return {"success": success}


@router.get("/search")
def search_in_files(keyword: str, infiniDocToken: Annotated[str | None, Header()] = None):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)

    resp = requests.post("http://localhost:8005/query", json={
        "query_text": keyword, "unique_id": unique_id})
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code,
                            detail="Error in query")
    result: dict = resp.json()
    keys = result.keys()
    fname_sha256 = filel.getFileNames(
        mysql_connection, unique_id, keys)
    dic = {}
    for i in range(len(fname_sha256)):
        dic[fname_sha256[i][1]] = fname_sha256[i][0]
    res = {}
    for i in keys:
        res[dic[i]] = result[i]
    mysql_connection.close()
    return {"result": res}
