from openai import OpenAI, AsyncOpenAI
from typing import AsyncGenerator
import os
from schemas import chatRequest
import authenticate
import filel
import requests
from fastapi import HTTPException


def get_models(endpoint, api_key):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=endpoint
        ) if api_key != "" else OpenAI(
            base_url=endpoint
        )
        models = client.models.list()
        return models
    except Exception as e:
        return []


async def get_ai_response(message: str, client: AsyncOpenAI, model: str) -> AsyncGenerator[str, None]:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant, skilled in explaining "
                    "complex concepts in simple terms."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield content


def get_ai_response_primary(title: str, paragraph_title: str, cur_content: str, user_prompt: str, client: OpenAI, model: str):
    msg = [
        {
            "role": "system",
            "content": (
                    "用户正在写一篇标题为'"
                    f"{title}".strip() +
                    "'的综述，他正在写一个标题为'"
                    f"{paragraph_title}".strip() + "'."
                    "的段落，现在的内容是 ["
                    f"{cur_content}".strip() + "]"
                    "，他的要求是：["
                    f"{user_prompt}".strip() + "]。\n"
                    "用户提供了论文库，如果你需要或用户提出要求参考，请输出你的搜索关键词（例如：“x关于y的观点”，或关键词。禁止使用“x的观点”，无法精确搜索） 每行一个，最多4个，请输出可能对你最有帮助的。系统将搜索。\n"
                    "如果你认为你不需要数据库，请回复英文 'No'，不要回复其他内容。"
            ),
        }
    ]
    response = client.chat.completions.create(
        model=model,
        messages=msg,
        stream=False,
    )

    return msg, response.choices[0].message.content


async def get_ai_response_secondary(title: str, paragraph_title: str, cur_content: str, user_prompt: str, additional_info_s: str, client: AsyncOpenAI, model: str) -> AsyncGenerator[str, None]:
    # additional_info like {'title, chunk 1-3':'content 1-3', 'title, chunk 4-5':'content 4-5'}
    additional_prompt = "The user has provided a paper database, please use the following to write the paragraph. " + \
        f"{additional_info_s}" + \
        "Note the database is just for reference, you should not just summary, write something ON YOUR OWN. If you need to cite, use latex format \\cite with given document ID." if additional_info_s != "" else ""
    msg = [
        {
            "role": "system",
            "content": (
                f"{additional_prompt}"
                "The user is writing an academic paper titled '"
                    f"{title}".strip() +
                    "' and the user is writing a paragraph titled '"
                    f"{paragraph_title}".strip() + "'."
                    "Current content of the paragraph is: ["
                    f"{cur_content}".strip() + "]."
                    "The requirement of the user is: ["
                    f"{user_prompt}".strip() + "]."
                    " Now please write the paragraph. Follow the language of the requirement of the user(to infer the user's language). WRITE THE FULL PARAGRAPH, do not add any extra information."
            ),
        }
    ]
    response = await client.chat.completions.create(
        model=model,
        messages=msg,
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield content


async def chat_project(req: chatRequest,  infiniDocToken: str):
    mysql_connection = authenticate.gen_mysql_connection_and_validate_token(
        infiniDocToken)
    # todo implement chat
    # response = req.user_prompt+" received"
    unique_id = authenticate.getUniqueID(mysql_connection, infiniDocToken)
    settings = authenticate.getSettings(mysql_connection, unique_id)
    if settings["endpoint"] == "":
        raise HTTPException(status_code=400, detail="Endpoint not set")
    if settings["model"] == "":
        raise HTTPException(status_code=400, detail="Model not set")
    client = OpenAI(
        api_key=settings["key"],
        base_url=settings["endpoint"]
    ) if settings["key"] != "" else OpenAI(
        base_url=settings["endpoint"]
    )
    msg, response = get_ai_response_primary(
        req.project_name, req.paragraph_title, req.paragraph_current_content, req.user_prompt, client, settings[
            "model"]
    )
    yield "--SYSTEM--"
    yield msg[0]["content"]
    yield "--DONE--"
    yield "--AI PROG--"
    if response == "No":
        yield "无需数据库"
    else:
        yield response
    yield "--DONE--"
    respobj = response.splitlines()
    kwds = [s.strip() for s in respobj]
    additional_info_s = ""
    if kwds[0] != "No":
        yield "--SYSTEM--"
        resp = requests.post("http://localhost:8005/querymultiple", json={
            "query_texts": kwds, "unique_id": unique_id, "filters": req.refs})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code,
                                detail="Error in query")
        result: dict = resp.json()
        keys = result.keys()
        # fname_sha256 = filel.getFileNames(
        #     mysql_connection, unique_id, keys)
        # dic = {}
        # for i in range(len(fname_sha256)):
        #     dic[fname_sha256[i][1]] = fname_sha256[i][0]
        # res = {}
        # for i in keys:
        #     res[dic[i]] = result[i]
        for i in keys:
            additional_info_s += "Document ID: " + i[:10] + \
                " (you need to use this for cite):\n"
            for j in result[i].keys():
                additional_info_s += "In " + j + ":\n" + result[i][j] + "\n"
        additional_info_s += "\n"
        yield additional_info_s
        yield "--DONE--"
    client2 = AsyncOpenAI(
        api_key=settings["key"],
        base_url=settings["endpoint"]
    ) if settings["key"] != "" else AsyncOpenAI(
        base_url=settings["endpoint"]
    )
    yield "--AI--"
    # get_ai_response_secondary is async function
    async for text in get_ai_response_secondary(req.project_name, req.paragraph_title, req.paragraph_current_content, req.user_prompt,
                                                additional_info_s,  client2, settings["model"]):
        yield text
    yield "--DONE--"
    yield "--DDONE--"
