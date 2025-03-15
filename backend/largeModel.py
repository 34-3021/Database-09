from openai import OpenAI
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
