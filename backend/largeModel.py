from openai import OpenAI, AsyncOpenAI
from typing import AsyncGenerator
import os


def get_models(endpoint, api_key):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=endpoint
        )
        models = client.models.list()
        return models
    except Exception as e:
        return []


def get_ai_response_primary(title: str, paragraph_title: str, cur_content: str, user_prompt: str, client: OpenAI, model: str):
    msg = [
        {
            "role": "system",
            "content": (
                    "The user is writing an academic paper titled '"
                    f"{title}".strip() +
                    "' and the user is writing a paragraph titled '"
                    f"{paragraph_title}".strip() + "'."
                    "Current content of the paragraph is: ["
                    f"{cur_content}".strip() + "]."
                    "The requirement of the user is: ["
                    f"{user_prompt}".strip() + "]."
                    "The user has provided a paper database, please reply with keywords(or phrases), one per line max 8, that are possibly helpful for you to write the paragraph."
                    "Please DO NOT write any content in this message."
                    "If you think you don't need the paper database (eg. the user is asking you to simply correct the grammar), please reply with 'No'."
            ),
        }
    ]
    response = client.chat.completions.create(
        model=model,
        messages=msg,
        stream=False,
    )

    return msg, response.choices[0].message.content


async def get_ai_response_secondary(additional_info_s: str, msg: list, client: AsyncOpenAI, model: str) -> AsyncGenerator[str, None]:
    # additional_info like {'title, chunk 1-3':'content 1-3', 'title, chunk 4-5':'content 4-5'}
    msg.append(
        {
            "role": "system",
            "content": (
                "The following are the paper database provided by the user, please use them to write the paragraph."
                f"{additional_info_s}"
                "Now please write or modify the paragraph. output in full, do not add any extra information."
            ),
        }
    )
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
