from langchain.retrievers import WeaviateHybridSearchRetriever
from weaviate import EmbeddedOptions
import weaviate
import os

client = weaviate.Client(
    embedded_options=EmbeddedOptions(),
    additional_headers={
        "X-OpenAI-Api-BaseURL": "https://api.openai.com/",
        "X-OpenAI-Api-Key": os.environ['OPENAI_API_KEY'],  # Replace this with your actual key
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
