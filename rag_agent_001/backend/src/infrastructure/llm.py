import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

def get_embeddings():
    hf_token = os.getenv("HF_TOKEN")
    return HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-small",
        model_kwargs={'token': hf_token} if hf_token else {}
    )

def get_llm():
    openrouter_api = os.getenv("OPENROUTER_API")
    if not openrouter_api:
        raise ValueError("❌ OPENROUTER_API не найден в .env")
    return ChatOpenAI(
        model="google/lyria-3-pro-preview",
        openai_api_key=openrouter_api,
        base_url="https://openrouter.ai/api/v1",
        max_retries=3
    )
