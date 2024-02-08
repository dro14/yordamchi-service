from langchain_community.retrievers import WeaviateHybridSearchRetriever
from weaviate.embedded import EmbeddedOptions
import weaviate
import os

users = {}

client = weaviate.Client(
    embedded_options=EmbeddedOptions(),
    additional_headers={
        "X-OpenAI-Api-BaseURL": "https://api.openai.com/",
        "X-OpenAI-Api-Key": os.environ['OPENAI_API_KEY'],
    }
)

retriever = WeaviateHybridSearchRetriever(
    client=client,
    index_name="LangChain",
    text_key="text",
    alpha=0.5,
    k=3,
    attributes=[],
    create_schema_if_missing=True,
)


def clear(user_id: int) -> None:
    try:
        user = users[user_id]
    except KeyError:
        pass
    else:
        for uuid in user["uuids"]:
            client.data_object.delete(uuid, class_name="LangChain")
        users.pop(user_id)
