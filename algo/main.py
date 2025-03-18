from typing import Annotated, Union

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import File, UploadFile, Header, BackgroundTasks
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from pypdf import PdfReader

import keys

client = chromadb.PersistentClient(path="./userdata/db")

app = FastAPI()

embedding_f = embedding_functions.OpenAIEmbeddingFunction(
    api_key=keys.api_key,
    api_base=keys.api_base,
    model_name="text-embedding-v3"
)

app.add_middleware(
    CORSMiddleware,
    # Adjust this to the specific origins you want to allow
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Fname, Content-Disposition"]
)


class ProcessRequest(BaseModel):
    filename: str
    unique_id: str


def processfile(fname: str, filename: str, unique_id: str):
    collection = client.get_or_create_collection(name=unique_id,
                                                 embedding_function=embedding_f)
    reader = PdfReader(filename)
    number_of_pages = len(reader.pages)
    text_all = ""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text = page.extract_text()
        text_all += text

    # remove all \n
    text_all = text_all.replace("\n", " ")
    # remove all \r
    text_all = text_all.replace("\r", " ")
    # sep with . to make it a sentence
    sentences = text_all.split(".")
    sentence_groups = []
    sentence_groups_ids = []
    cur_sentence = ""
    i = 0
    for sentence in sentences:
        if len(cur_sentence) + len(sentence) < 5000:
            cur_sentence += sentence
        else:
            sentence_groups.append(cur_sentence)
            sentence_groups_ids.append(fname+"_"+str(i))
            i += 1
            cur_sentence = sentence
    sentence_groups.append(cur_sentence)
    sentence_groups_ids.append(fname+"_"+str(i))

    collection.add(documents=sentence_groups, ids=sentence_groups_ids)

    with open("./log.txt", "w", encoding="utf-8") as f:
        for sentence_chunk in sentence_groups:
            f.write(sentence_chunk)
            f.write("\n")
            f.write("\n")

    return


@app.get("/")
def read_root():
    raise HTTPException(
        status_code=403, detail="Accessing the root is not allowed")


@app.post("/process")
async def process(request: ProcessRequest, background_tasks: BackgroundTasks):
    fname = request.filename
    filename = f"./userdata/files/{fname[0:2]}/{fname}.dat"

    background_tasks.add_task(processfile, fname, filename, request.unique_id)
    return {"filename": fname}
