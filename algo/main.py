from typing import Annotated, Union, AsyncGenerator

from fastapi import FastAPI, WebSocket
from fastapi import HTTPException
from fastapi import File, UploadFile, Header, BackgroundTasks
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from pypdf import PdfReader


import keys

client = chromadb.PersistentClient(path="./userdata/db")

openai_clients = {}

app = FastAPI()

embedding_f = embedding_functions.OpenAIEmbeddingFunction(
    api_key=keys.api_key,
    api_base=keys.api_base,
    model_name=keys.model_name
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


class QueryRequest(BaseModel):
    unique_id: str
    query_text: str


class QueryMultiRequest(BaseModel):
    unique_id: str
    query_texts: list[str]
    filters: list[str]


class UniqueId(BaseModel):
    unique_id: str


class generateRequest(BaseModel):
    unique_id: str
    llm_endpoint: str
    llm_key: str
    prompt: str
    paragraph_title: str


def extractauthor(chunk: str):
    llmclient = OpenAI(
        api_key=keys.llm_api_key,
        base_url=keys.llm_api_base
    )
    # attempt to extract the author from the first chunk
    prompt = "以下为某篇论文 PDF 提取出的第一段内容，如果你觉得可以提取出作者信息，请提取出作者信息，格式为：“人名、人名”\n\n如果你觉得无法提取出作者信息，请回复“不详”。\n\n内容如下：\n\n" + \
        chunk + "\n\n 仅包括人名或“不详”。不要回复多余信息"
    response = llmclient.chat.completions.create(
        model=keys.llm_model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=False,
    )
    return response.choices[0].message.content.strip()


def processfile(fname: str, filename: str, unique_id: str):
    collection = client.get_or_create_collection(name=unique_id,
                                                 embedding_function=embedding_f)
    reader = PdfReader(filename, strict=False)
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
    # remove all \x00
    text_all = text_all.replace("\x00", " ")
    # sep with . ? ！ 。 ! ？ to make it a sentence
    sentences = [s.strip() for s in text_all.replace('?', '.').replace('？', '.').replace(
        '。', '.').replace('!', '.').replace('！', '.').split('.') if s.strip()]
    sentence_groups = []
    sentence_groups_ids = []
    metadatas = []
    cur_sentence = ""
    i = 0
    for sentence in sentences:
        if len(cur_sentence) + len(sentence) < 500:
            cur_sentence += sentence
        else:
            sentence_groups.append(cur_sentence)
            sentence_groups_ids.append(fname+"_"+str(i))
            metadatas.append({"filename": fname})
            i += 1
            cur_sentence = sentence
    sentence_groups.append(cur_sentence)
    sentence_groups_ids.append(fname+"_"+str(i))
    metadatas.append({"filename": fname})
    # extract author from the first chunk
    author = ""
    if len(sentence_groups) > 0:
        author_ = extractauthor(sentence_groups[0])
        if author_ != "作者不详":
            author = author_
    # add author to the start of each chunk
    for i in range(len(sentence_groups)):
        if author != "":
            sentence_groups[i] = author + "： " + sentence_groups[i]
        else:
            sentence_groups[i] = sentence_groups[i]

    for i in range(0, len(sentence_groups), 10):
        collection.add(documents=sentence_groups[i:i+10],
                       ids=sentence_groups_ids[i:i+10],
                       metadatas=metadatas[i:i+10]
                       )

    with open("./log.txt", "w", encoding="utf-8") as f:
        for sentence_chunk in sentence_groups:
            f.write(sentence_chunk)
            f.write("\n")
            f.write("\n")

        for id in sentence_groups_ids:
            f.write(id)
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


@app.post("/query")
async def query(request: QueryRequest):
    collection = client.get_or_create_collection(
        name=request.unique_id, embedding_function=embedding_f)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Perform a search for top 10 similar sentences
    query_text = request.query_text
    results = collection.query(query_texts=[query_text], n_results=10)

    ids = results["ids"][0]
    # get top 3
    top3 = ids[:3]

    query_passages = {}
    # format xxxxxx_k
    for id in top3:
        idx = id.split("_")[0]
        # check if id exists
        if idx not in query_passages:
            query_passages[idx] = []
        chunk = int(id.split("_")[1])
        chunkbegin = max(0, chunk-1)
        chunkend = chunk+1
        for i in range(chunkbegin, chunkend):
            query_passages[idx].append(str(i))

    resultx = {}

    for key in query_passages:
        # remove duplicates
        query_passages[key] = list(set(query_passages[key]))
        resultx[key] = collection.get(
            ids=[key+"_"+chk for chk in query_passages[key]])

    # get all the sentences

    final_result = {}

    for key in resultx:
        # Group continuous chunks and format the result
        chunks = sorted([int(chunk.split("_")[1])
                        for chunk in resultx[key]["ids"]])
        grouped_chunks = []
        current_group = [chunks[0]]

        for i in range(1, len(chunks)):
            if chunks[i] == chunks[i - 1] + 1:
                current_group.append(chunks[i])
            else:
                grouped_chunks.append(current_group)
                current_group = [chunks[i]]

        grouped_chunks.append(current_group)

        final_result[key] = {}
        for group in grouped_chunks:
            chunk_range = f"chunk {group[0]} - {group[-1]}" if len(
                group) > 1 else f"chunk {group[0]}"
            sentences = " ".join(resultx[key]["documents"][resultx[key]["ids"].index(
                f"{key}_{chunk}")] for chunk in group)
            final_result[key][chunk_range] = sentences
        pass

    return final_result


@app.post("/querymultiple")
async def querymultiple(request: QueryMultiRequest):
    collection = client.get_or_create_collection(
        name=request.unique_id, embedding_function=embedding_f)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Perform a search for top 10 similar sentences
    query_texts = request.query_texts

    filter = {
        "filename": {
            "$in": request.filters
        }
    }

    query_passages = {}
    for query_text in query_texts:
        results = collection.query(
            query_texts=[query_text], n_results=3, where=filter)
        ids = results["ids"][0]

        # format xxxxxx_k
        for id in ids:
            idx = id.split("_")[0]
            # check if id exists
            if idx not in query_passages:
                query_passages[idx] = []
            chunk = int(id.split("_")[1])
            chunkbegin = max(0, chunk-1)
            chunkend = chunk+1
            for i in range(chunkbegin, chunkend):
                query_passages[idx].append(str(i))

    resultx = {}

    for key in query_passages:
        # remove duplicates
        query_passages[key] = list(set(query_passages[key]))
        resultx[key] = collection.get(
            ids=[key+"_"+chk for chk in query_passages[key]])

    # get all the sentences

    final_result = {}

    for key in resultx:
        # Group continuous chunks and format the result
        chunks = sorted([int(chunk.split("_")[1])
                        for chunk in resultx[key]["ids"]])
        grouped_chunks = []
        current_group = [chunks[0]]

        for i in range(1, len(chunks)):
            if chunks[i] == chunks[i - 1] + 1:
                current_group.append(chunks[i])
            else:
                grouped_chunks.append(current_group)
                current_group = [chunks[i]]

        grouped_chunks.append(current_group)

        final_result[key] = {}
        for group in grouped_chunks:
            chunk_range = f"chunk {group[0]} - {group[-1]}" if len(
                group) > 1 else f"chunk {group[0]}"
            sentences = " ".join(resultx[key]["documents"][resultx[key]["ids"].index(
                f"{key}_{chunk}")] for chunk in group)
            final_result[key][chunk_range] = sentences
        pass

    return final_result


@app.post("/deleteall")
async def delete(request: UniqueId):
    client.delete_collection(name=request.unique_id)
    return {"status": "deleted"}


@app.post("/delete")
async def delete(request: ProcessRequest):
    collection = client.get_or_create_collection(
        name=request.unique_id, embedding_function=embedding_f)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection.delete(where={"filename": request.filename})
